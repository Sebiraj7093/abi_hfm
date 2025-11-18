"""
Orchestration Layer - Deep Agent with Sub-Agents

Handles:
1. Deep Agent orchestration
2. Planning and task decomposition
3. Sub-agent delegation (SQL Agent, RAG Agent)
4. Response synthesis
"""

import asyncio
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import os
import webbrowser
from datetime import datetime
from rag_agent_core import RAGAgent
# LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from deepagents import create_deep_agent

# Import existing sub-agents
from app.services.sql_agent_core import agent as sql_agent, init_db_pool, cleanup_db_pool
from app.services.rag_agent_core import RAGAgent, load_csv_files

load_dotenv()

# ============================================================================
# SUB-AGENT REGISTRY
# ============================================================================

SUBAGENTS = {
    "sql-agent": {
        "name": "SQL Agent",
        "description": "Expert in querying HFM trading database. Analyzes forex trades, calculates profits/losses, finds patterns, and generates visualizations.",
        "prompt": """You are the SQL Agent - an expert database analyst for HFM trading data.
        
Your capabilities:
- Query PostgreSQL trading database
- Calculate PnL, profits, losses, win rates
- Analyze trading patterns and trends
- Generate statistical insights
- Create data visualizations

Always provide precise, data-driven answers with specific numbers and metrics.""",
        "use_for": [
            "Profit/loss calculations",
            "Trading statistics and metrics",
            "Historical trade analysis",
            "Performance over time",
            "Currency pair comparisons",
            "Win rate and success metrics",
            "Data visualizations"
        ],
        "tools": ["database_query", "calculate_metrics", "generate_charts"]
    },
    "rag-agent": {
        "name": "Knowledge Base Agent",
        "description": "Expert with access to HFM documentation, FAQs, and support articles. Answers questions about platform features, trading concepts, and procedures.",
        "prompt": """You are the RAG Agent - an expert in HFM platform knowledge and trading concepts.

Your capabilities:
- Search HFM documentation and FAQs
- Explain trading concepts and terminology
- Provide step-by-step procedures
- Answer platform feature questions
- Retrieve relevant support articles

Always provide clear, accurate, and helpful information from the knowledge base.""",
        "use_for": [
            "Account opening procedures",
            "Trading platform features",
            "Trading concepts (leverage, margin, etc.)",
            "Verification processes",
            "Payment methods",
            "Platform navigation",
            "General trading questions"
        ],
        "tools": ["search_knowledge_base", "retrieve_documents"]
    }
}

def list_available_agents() -> str:
    """List all available sub-agents and their capabilities"""
    output = "Available Sub-Agents:\n\n"
    for agent_id, info in SUBAGENTS.items():
        output += f"{info['name']}\n"
    return output

# ============================================================================
# VIRTUAL FILE SYSTEM
# ============================================================================

virtual_file_system: Dict[str, str] = {}

def file_write(filename: str, content: str) -> str:
    """Write to virtual file system"""
    virtual_file_system[filename] = content
    return f"Saved: {filename}"

def file_read(filename: str) -> str:
    """Read from virtual file system"""
    return virtual_file_system.get(filename, f"Not found: {filename}")

# ============================================================================
# SUB-AGENT INITIALIZATION
# ============================================================================

_rag_agent_instance: Optional[RAGAgent] = None
_agents_initialized = False

async def initialize_sub_agents():
    """Initialize SQL and RAG sub-agents"""
    global _rag_agent_instance, _agents_initialized
    
    if _agents_initialized:
        return
    
    await init_db_pool()
    
    _rag_agent_instance = RAGAgent()
    await _rag_agent_instance.initialize()
    await load_csv_files(_rag_agent_instance)
    
    _agents_initialized = True



# ============================================================================
# Tool 2 - SUB-AGENT DELEGATION TOOLS
# ============================================================================

@tool
async def call_sql_agent(query: str) -> str:
    """
    Delegate to SQL Agent for trading database queries.
    Automatically generates and displays charts when appropriate.
    
    The SQL Agent specializes in:
    - Profit/loss calculations
    - Trading statistics and metrics
    - Historical trade analysis
    - Performance over time
    - Currency pair comparisons
    - Win rate and success metrics
    - Data visualizations
    
    Args:
        query: Trading data question
    
    Returns:
        SQL Agent's analysis (with chart auto-generated if applicable)
    """
    await initialize_sub_agents()
    
    try:
        # Store query for potential chart generation
        import SQL_Agent
        SQL_Agent.LAST_USER_QUERY = query
        
        response = await sql_agent.ainvoke({
            "messages": [{"role": "user", "content": query}]
        })
        
        messages = response.get("messages", [])
        for message in reversed(messages):
            if hasattr(message, 'content') and message.content:
                result = message.content
                file_write("sql_results.txt", result)
                
                # Auto-generate and display chart if recommended
                if any(keyword in result.lower() for keyword in [
                    "chart has been generated",
                    "visualization",
                    "[visualization",
                    "graph has been created"
                ]):
                    try:
                        # Import chart generator
                        from app.services.sql_agent_core import LAST_QUERY_RESULTS, ChartGenerator
                        
                        if LAST_QUERY_RESULTS:
                            print("\nGenerating visualization...")
                            
                            # Generate chart
                            fig = ChartGenerator.create_visualization(
                                LAST_QUERY_RESULTS,
                                query
                            )
                            
                            if fig:
                                # Save as HTML with timestamp
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                chart_file = f"chart_{timestamp}.html"
                                fig.write_html(chart_file)
                                
                                # Auto-open in browser
                                import webbrowser
                                webbrowser.open(chart_file)
                                
                                print(f"Chart saved and opened: {chart_file}\n")
                                
                                # Update response
                                result += f"\n\nInteractive chart opened in browser: {chart_file}"
                            else:
                                print("Chart generation returned None\n")
                    
                    except Exception as e:
                        print(f"Chart generation error: {e}\n")
                        result += f"\n\nNote: Chart generation encountered an error: {str(e)}"
                
                return result
            
            elif isinstance(message, dict) and message.get("content"):
                result = message.get("content")
                file_write("sql_results.txt", result)
                return result
        
        return "SQL Agent returned no response."
    
    except Exception as e:
        return f"SQL Agent error: {str(e)}"

@tool
async def call_rag_agent(query: str) -> str:
    """
    Delegate to RAG Agent for knowledge base search.
    Returns search results directly for the orchestrator to use.
    
    The RAG Agent specializes in:
    - Account opening procedures
    - Trading platform features
    - Trading concepts (leverage, margin, etc.)
    - Verification processes
    - Payment methods
    - Platform navigation
    - General trading questions
    
    Args:
        query: Trading knowledge question
    
    Returns:
        Search results from knowledge base
    """
    await initialize_sub_agents()
    
    try:
        # Direct vector search - return raw results
        search_results = await _rag_agent_instance.vector_store.search_dual_ranked(query, k=5)
        
        if not search_results:
            return "No relevant information found in knowledge base."
        
        # Format results for orchestrator
        output = "Knowledge Base Results:\n\n"
        for i, result in enumerate(search_results, 1):
            output += f"[{i}] Question: {result['question']}\n"
            output += f"    Answer: {result['answer']}\n\n"
        
        file_write("rag_results.txt", output)
        return output
        
    except Exception as e:
        return f"RAG Agent error: {str(e)}"

# ============================================================================
# DEEP AGENT ORCHESTRATOR
# ============================================================================

DEEP_AGENT_PROMPT = """You are the HFM Digital Assistant Orchestrator - an intelligent Deep Agent coordinating specialized sub-agents.

YOUR ARCHITECTURE:

You are a PLANNING and DELEGATION agent with two specialized sub-agents:
1. SQL Agent - Trading database expert (call_sql_agent)
   - Use for: profits, losses, trades, statistics, metrics, performance data
   - Returns: Direct analysis and data
   
2. RAG Agent - Knowledge base search (call_rag_agent)
   - Use for: concepts, procedures, how-tos, platform features, explanations
   - Returns: Search results from knowledge base that YOU must synthesize

YOUR WORKFLOW:

For GREETINGS:
- Respond directly without calling sub-agents

For SIMPLE queries (single sub-agent needed):
1. Identify which sub-agent to call
2. Call the appropriate sub-agent
3. For SQL Agent: Return response directly
4. For RAG Agent: Read the search results and synthesize a clear answer

For COMPLEX queries (multi-step or both sub-agents):
1. Create a plan using todo_write
2. Execute subtasks by calling sub-agents
3. Update progress with update_todo
4. Synthesize results into comprehensive answer

ROUTING RULES:

Call SQL Agent when query involves:
- Numbers, calculations, metrics
- "What's my profit/loss?"
- "Show me trades"
- "Calculate my win rate"
- "How much did I make?"
- Keywords: profit, loss, trades, calculate, show, total, win rate

Call RAG Agent when query involves:
- Concepts, definitions, explanations
- "What is leverage?"
- "How do I verify my account?"
- "Explain margin trading"
- "How to open an account?"
- Keywords: what is, how to, explain, procedure, definition
- NOTE: RAG Agent returns search results - YOU must synthesize the answer

Call BOTH when query needs data AND explanation:
- "Show my profit and explain what affects it"
- "Calculate my win rate and tell me if it's good"

PLANNING GUIDELINES:

Simple query example:
User: "What's my total profit?"
-> Just call_sql_agent("What's my total profit?")

Complex query example:
User: "Analyze my trading performance and suggest improvements"
-> todo_write(["Get trading statistics", "Get best practices", "Synthesize recommendations"])
-> call_sql_agent("Analyze my trading performance with key metrics")
-> update_todo("Get trading statistics")
-> call_rag_agent("What are trading best practices for improvement?")
-> update_todo("Get best practices")
-> Synthesize both into actionable recommendations
-> update_todo("Synthesize recommendations")

BEST PRACTICES:

DO:
- Respond directly to greetings without calling sub-agents
- Use todo_write for multi-step queries
- Call the right sub-agent based on query type
- For SQL Agent: Return the response as-is
- For RAG Agent: Read the search results and provide a clear, synthesized answer
- Update tasks as you complete them
- Synthesize when combining multiple sources

DON'T:
- Call sub-agents for simple greetings (hi, hello, hey)
- Try to answer trading questions without calling sub-agents
- Return raw search results from RAG Agent - always synthesize them
- Add unnecessary commentary
- Call both agents when one is sufficient
- Forget to create a plan for complex queries

IMPORTANT FOR RAG QUERIES:
- When call_rag_agent returns results, YOU must read them and provide the answer
- Don't just repeat the search results - extract the relevant answer
- If no relevant results, say "I don't have that information"

Remember: You coordinate experts. Plan, delegate, synthesize.
"""

# Global orchestration agent
_orchestration_agent = None

async def initialize_orchestration():
    """Initialize the orchestration agent and sub-agents"""
    global _orchestration_agent
    
    if _orchestration_agent is not None:
        return
    
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=api_key,
        max_output_tokens=2000
    )
    
    tools = [

        call_sql_agent,
        call_rag_agent
    ]
    
    _orchestration_agent = create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=DEEP_AGENT_PROMPT
    )
    
    await initialize_sub_agents()
    
async def orchestration_handle(user_query: str) -> str:
    """
    Handle user query through Deep Agent orchestration.
    
    Args:
        user_query: The user's trading-related question
    
    Returns:
        Response from orchestration agent
    """
    if _orchestration_agent is None:
        await initialize_orchestration()
    
    try:
        response = await _orchestration_agent.ainvoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        
        messages = response.get("messages", [])
        for message in reversed(messages):
            if hasattr(message, 'content') and message.content:
                return message.content
            elif isinstance(message, dict) and message.get("content"):
                return message.get("content")
        
        return "No response generated."
    
    except Exception as e:
        return f"Orchestration error: {str(e)}"

# ============================================================================
# CLEANUP
# ============================================================================

async def cleanup_orchestration():
    """Cleanup orchestration resources"""
    await cleanup_db_pool()

# ============================================================================
# STANDALONE TESTING
# ============================================================================

async def test_orchestration():
    """Test orchestration agent standalone"""
    
    await initialize_orchestration()
    
    print("=" * 70)
    print("Orchestration Agent - Standalone Test")
    print("=" * 70)
    print("\nType 'exit' to quit\n")
    
    while True:
        try:
            user_input = input("Query: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            if not user_input:
                continue
            
            response = await orchestration_handle(user_input)
            print(f"\nResponse: {response}\n")
            print("-" * 70 + "\n")
        
        except KeyboardInterrupt:
            break
    
    await cleanup_orchestration()

if __name__ == "__main__":
    asyncio.run(test_orchestration())
