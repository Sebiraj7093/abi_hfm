"""
Clean FastAPI Application for HFM RAG Chatbot
Uses Deep Agent with RAG and SQL subagents
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import agents
from app.services_v1.rag_agent_core import RAGAgent, load_csv_files
from app.services_v1.sql_agent_core import sql_agent, init_db_pool, cleanup_db_pool
from app.services_v1.constants import DEEP_AGENT_PROMPT

# Import LangChain and DeepAgents
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent, CompiledSubAgent

load_dotenv()

# Global instances
deep_agent = None
rag_agent_instance = None


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    success: bool
    response: str
    query: Optional[str] = None
    session_id: Optional[str] = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global deep_agent, rag_agent_instance
    
    # Startup
    print("🚀 Starting HFM Deep Agent Chatbot...")
    try:
        # Get API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key,
            max_output_tokens=2000
        )
        
        # Initialize SQL Agent DB Pool
        print("🔧 Initializing SQL Agent database pool...")
        await init_db_pool()
        
        # Initialize RAG Agent
        print("🔧 Initializing RAG Agent...")
        rag_agent_instance = RAGAgent()
        await rag_agent_instance.initialize()
        await load_csv_files(rag_agent_instance)
        
        # Create RAG SubAgent
        rag_subagent = CompiledSubAgent(
            name="RAG_Agent",
            description="RAG Agent for Q&A for any query related to HFM or trading from the user",
            runnable=rag_agent_instance.agent
        )
        
        # Create SQL SubAgent
        sql_subagent = CompiledSubAgent(
            name="SQL_Agent",
            description="SQL Agent for any query related to user's trading data and metrics",
            runnable=sql_agent
        )
        
        # Create Deep Agent with both subagents
        print("🤖 Creating Deep Agent with RAG and SQL subagents...")
        deep_agent = create_deep_agent(
            model=llm,
            subagents=[rag_subagent, sql_subagent],
            system_prompt=DEEP_AGENT_PROMPT
        )
        
        print("✅ Deep Agent initialized successfully with RAG and SQL subagents")
    except Exception as e:
        print(f"❌ Failed to initialize Deep Agent: {e}")
        raise
    
    yield
    
    # Shutdown
    print("👋 Shutting down HFM Deep Agent Chatbot...")
    await cleanup_db_pool()


# Create FastAPI app
app = FastAPI(
    title="HFM Deep Agent Chatbot API",
    description="AI-powered chatbot with RAG and SQL agents for HFM trading platform",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Serve the UI
@app.get("/")
async def serve_ui():
    """Serve the chat UI"""
    return FileResponse("app/static/index.html")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "HFM Deep Agent Chatbot",
        "deep_agent_ready": deep_agent is not None,
        "subagents": ["RAG_Agent", "SQL_Agent"]
    }


# Main query endpoint for UI
@app.post("/api/v1/query", response_model=QueryResponse)
async def query_deep_agent(request: QueryRequest):
    """
    Query the Deep Agent with RAG and SQL subagents (UI endpoint)
    
    The Deep Agent will automatically:
    - Route knowledge questions to RAG Agent
    - Route trading data queries to SQL Agent
    - Combine both when needed
    
    Args:
        request: QueryRequest with query and optional session_id
    
    Returns:
        QueryResponse with success and response
    """
    if deep_agent is None:
        raise HTTPException(status_code=503, detail="Deep agent not initialized")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Query the deep agent
        response = await deep_agent.ainvoke({
            "messages": [{"role": "user", "content": request.query}]
        })
        
        # Extract answer from response
        messages = response.get("messages", [])
        answer = "I couldn't generate a response."
        
        for message in reversed(messages):
            if hasattr(message, 'content') and message.content:
                answer = message.content
                break
            elif isinstance(message, dict) and message.get("content"):
                answer = message.get("content")
                break
        
        return QueryResponse(
            success=True,
            response=answer,
            query=request.query,
            session_id=request.session_id
        )
    
    except Exception as e:
        return QueryResponse(
            success=False,
            response=f"Error processing query: {str(e)}",
            query=request.query,
            session_id=request.session_id
        )


# Root endpoint
@app.get("/api")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "HFM Deep Agent Chatbot API",
        "version": "2.0.0",
        "agents": {
            "rag_agent": "Knowledge base search for HFM/trading questions",
            "sql_agent": "Trading data analysis and metrics"
        },
        "endpoints": {
            "ui": "/",
            "health": "/health",
            "query": "/api/v1/query (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_main:app",
        host="0.0.0.0",  # Accessible from any network interface
        port=8080,        # Changed to port 8080
        reload=True
    )
