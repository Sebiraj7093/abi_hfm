"""
Fixed Deep Agents RAG System - Properly Working Search
"""

import os
import sys
import asyncio
import pandas as pd
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()




# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services_v1.constants import DEEP_AGENT_PROMPT
from app.services_v1.sql_agent_core import sql_agent

import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.tools import BaseTool
from deepagents import create_deep_agent
from langchain.agents import create_agent
from deepagents import CompiledSubAgent
class PGVectorStore:
    """pgvector implementation with working search"""
    
    def __init__(self, connection_string: str, embedding_model: str):
        self.connection_string = connection_string
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    async def initialize(self):
        """Initialize database tables"""
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qa_pairs (
                id SERIAL PRIMARY KEY,
                qa_id TEXT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                question_embedding vector(768),
                answer_embedding vector(768),
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS qa_question_embedding_idx 
            ON qa_pairs USING ivfflat (question_embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS qa_answer_embedding_idx 
            ON qa_pairs USING ivfflat (answer_embedding vector_cosine_ops)
            WITH (lists = 100)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS qa_qa_id_idx 
            ON qa_pairs (qa_id)
        """)
        
        conn.commit()
        cur.close()
        conn.close()
    
    async def add_qa_pairs(self, qa_pairs: List[Dict]):
        """Add Q&A pairs to database"""
        if not qa_pairs:
            return
        
        questions = [qa["question"] for qa in qa_pairs]
        answers = [qa["answer"] for qa in qa_pairs]
        
        question_embeddings = await self.embeddings.aembed_documents(questions)
        answer_embeddings = await self.embeddings.aembed_documents(answers)
        
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        
        for qa, q_emb, a_emb in zip(qa_pairs, question_embeddings, answer_embeddings):
            cur.execute("""
                INSERT INTO qa_pairs (qa_id, question, answer, question_embedding, answer_embedding, source)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                qa.get("qa_id"),
                qa["question"],
                qa["answer"],
                q_emb,
                a_emb,
                qa.get("source", "unknown")
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Added {len(qa_pairs)} Q&A pairs")
    
    async def get_qa_count(self):
        """Get total number of Q&A pairs"""
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM qa_pairs")
        count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return count
    
    async def check_file_loaded(self, csv_path: str):
        """Check if a specific CSV file has been loaded"""
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM qa_pairs 
            WHERE source = %s
        """, (csv_path,))
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count > 0
    
    async def search_by_qa_id(self, qa_id: str):
        """Search by QA ID"""
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT qa_id, question, answer, source
            FROM qa_pairs
            WHERE UPPER(qa_id) = UPPER(%s)
            LIMIT 1
        """, (qa_id,))
        
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        return dict(result) if result else None
    
    async def search_question(self, query: str, k: int = 5):
        """Search by question similarity"""
        query_embedding = await self.embeddings.aembed_query(query)
        
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        cur.execute("""
            SELECT 
                qa_id,
                question, 
                answer,
                source,
                1 - (question_embedding <=> %s::vector) as similarity
            FROM qa_pairs
            ORDER BY question_embedding <=> %s::vector
            LIMIT %s
        """, (embedding_str, embedding_str, k))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(result) for result in results]
    
    async def search_answer(self, query: str, k: int = 5):
        """Search by answer similarity"""
        query_embedding = await self.embeddings.aembed_query(query)
        
        conn = psycopg2.connect(self.connection_string)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        cur.execute("""
            SELECT 
                qa_id,
                question, 
                answer,
                source,
                1 - (answer_embedding <=> %s::vector) as similarity
            FROM qa_pairs
            ORDER BY answer_embedding <=> %s::vector
            LIMIT %s
        """, (embedding_str, embedding_str, k))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(result) for result in results]
    
    async def search_dual_ranked(self, query: str, k: int = 5):
        """Dual search with ranking - questions weighted higher than answers"""
        # Search both questions and answers
        question_results = await self.search_question(query, k)
        answer_results = await self.search_answer(query, k)
        
        # Combine and re-rank with weights
        combined_results = {}
        
        # Add question results with higher weight (0.7)
        for result in question_results:
            qa_id = result['qa_id']
            weighted_score = result['similarity'] * 0.7
            combined_results[qa_id] = {
                **result,
                'final_score': weighted_score,
                'match_type': 'question'
            }
        
        # Add answer results with lower weight (0.3)
        for result in answer_results:
            qa_id = result['qa_id']
            weighted_score = result['similarity'] * 0.3
            
            if qa_id in combined_results:
                # Boost score if found in both
                combined_results[qa_id]['final_score'] += weighted_score
                combined_results[qa_id]['match_type'] = 'both'
            else:
                combined_results[qa_id] = {
                    **result,
                    'final_score': weighted_score,
                    'match_type': 'answer'
                }
        
        # Sort by final score and return top k
        sorted_results = sorted(
            combined_results.values(), 
            key=lambda x: x['final_score'], 
            reverse=True
        )[:k]
        
        return sorted_results

class CSVLoaderTool(BaseTool):
    """Load Q&A pairs from CSV"""
    
    name: str = "load_csv"
    description: str = "Load Q&A CSV file into the knowledge base. Expects CSV with 'user' (question) and 'standard_answer' (answer) columns."
    vector_store: Any = None
    
    def __init__(self, vector_store):
        super().__init__(vector_store=vector_store)
    
    def _run(self, csv_filename: str) -> str:
        return asyncio.run(self._arun(csv_filename))
    
    async def _arun(self, csv_filename: str) -> str:
        try:
            # Build full path - use project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_path = os.path.join(project_root, csv_filename)
            
            if not os.path.exists(csv_path):
                return f"❌ File not found: {csv_path}"
            
            # Check if already loaded
            if await self.vector_store.check_file_loaded(csv_path):
                return f"✅ File already loaded: {csv_filename}"
            
            # Load CSV
            df = pd.read_csv(csv_path)
            print(f"📊 Loading {csv_filename} with {len(df)} rows...")
            
            # Check required columns
            if 'user' not in df.columns or 'standard_answer' not in df.columns:
                return f"❌ CSV must have 'user' and 'standard_answer' columns. Found: {list(df.columns)}"
            
            # Build Q&A pairs
            qa_pairs = []
            for idx, row in df.iterrows():
                question = str(row['user']).strip()
                answer = str(row['standard_answer']).strip()
                
                if not question or not answer or question == 'nan' or answer == 'nan':
                    continue
                
                qa_id = f"Qa_{idx+1:03d}"  # Generate QA ID if not present
                if 'qa_id' in df.columns and not pd.isna(row['qa_id']):
                    qa_id = str(row['qa_id']).strip()
                
                qa_pairs.append({
                    "qa_id": qa_id,
                    "question": question,
                    "answer": answer,
                    "source": csv_path
                })
            
            # Add to database
            await self.vector_store.add_qa_pairs(qa_pairs)
            
            return f"✅ Loaded {len(qa_pairs)} Q&A pairs from {csv_filename}"
            
        except Exception as e:
            return f"❌ Error loading CSV: {str(e)}"

class SearchTool(BaseTool):
    """Search Q&A knowledge base"""
    
    name: str = "search_qa"
    description: str = "Search the Q&A knowledge base. Use this to find answers to user questions."
    vector_store: Any = None
    
    def __init__(self, vector_store):
        super().__init__(vector_store=vector_store)
    
    def _run(self, user_question: str) -> str:
        return asyncio.run(self._arun(user_question))
    
    async def _arun(self, user_question: str) -> str:
        try:
            # Check if it's a QA ID
            if user_question.strip().upper().startswith('QA_'):
                result = await self.vector_store.search_by_qa_id(user_question.strip())
                if result:
                    return self._format_single_result(result)
                return "No Q&A pair found with that ID."
            
            # Use dual search with ranking
            results = await self.vector_store.search_dual_ranked(user_question, k=5)
            
            if not results:
                return "No matching Q&A pairs found."
            
            return self._format_dual_results(results)
            
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _format_single_result(self, result: Dict) -> str:
        """Format single QA result"""
        return f"""Found Q&A Pair:
ID: {result['qa_id']}
Question: {result['question']}
Answer: {result['answer']}
Source: {result['source']}"""
    
    def _format_dual_results(self, results: List[Dict]) -> str:
        """Format dual search results - simplified for agent consumption"""
        if not results:
            return "No relevant information found."
        
        parts = ["Search Results:\n"]
        
        for i, result in enumerate(results, 1):
            parts.append(f"""[Result {i}]
Question: {result['question']}
Answer: {result['answer']}
""")
        
        return "\n".join(parts)

class RAGAgent:
    """Q&A RAG Agent"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.connection_string = os.getenv("PGVECTOR_CONNECTION")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        if not self.connection_string:
            raise ValueError("PGVECTOR_CONNECTION not found")
        
        self.vector_store = PGVectorStore(
            self.connection_string,
            "models/text-embedding-004"
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            temperature=0
        )
        
        self.agent = None
    
    async def initialize(self):
        """Initialize RAG system"""
        await self.vector_store.initialize()
        

        search_tool = SearchTool(self.vector_store)
        
        # In RAGAgent.initialize
        self.agent = create_agent(
            model=self.llm,
            tools=[search_tool],
            system_prompt="""You are a helpful and accurate Q&A assistant.

Your job is to answer the user's question based *only* on the context provided by the `search_qa` tool.

CRITICAL RULES:
1.  **ALWAYS** call the `search_qa` tool for every question.
2.  The tool will return a block of "Search Results" (the context).
3.  **Read the user's ORIGINAL question and the provided context carefully based on all the search results returns (chunks)**
4.  **Analyze the context:**
    * If one of the results (the `Answer` field) clearly and directly answers the user's question, provide that answer.
    * If the context is about a *different* topic (e.g., user asks for "joint account" but context is "trading account"), you MUST recognize this mismatch.
5.  If the context does *not* contain a relevant answer, or if the tool returns "No relevant information," you MUST respond with:
    "I'm sorry, I don't have that specific information in my knowledge base."
6.  Do NOT use any outside knowledge. Do not make up answers.
7.  Be polite and conversational. Do not mention the search tool, similarity scores, or "the context" in your final response.
"""
)      
        return self.agent
        


async def load_csv_files(rag):
    """Load CSV files if not already loaded"""
    csv_files = [
        "qa_pairs.csv",
        "qa_pairs_variations.csv",
        "web_questions.csv",
    ]
    
    qa_count = await rag.vector_store.get_qa_count()
    
    if qa_count > 0:
        return  # Silent if already loaded
    
    csv_loader = CSVLoaderTool(rag.vector_store)
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    for csv_file in csv_files:
        csv_path = os.path.join(project_root, csv_file)
        if os.path.exists(csv_path):
            await csv_loader._arun(csv_file)



if __name__ == "__main__":
    async def main():
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key,
            max_output_tokens=2000
        )
        
        # Initialize RAG agent
        rag = RAGAgent()
        await rag.initialize()
        
        # Load CSV files
        #await load_csv_files(rag)
        
        # Create sub-agent
        rag_subagent = CompiledSubAgent(
            name="RAG_Agent",
            description="RAG Agent for Q&A for any query related to hfm or trading from the user",
            runnable=rag.agent
        )
        sql_subagent = CompiledSubAgent(
            name="SQL_Agent",
            description="SQL Agent for any query related to user's trading data and metrics",
            runnable=sql_agent
        )
        # Create deep agent
        agent = create_deep_agent(
            model=llm,
            subagents=[rag_subagent, sql_subagent],    
            system_prompt=DEEP_AGENT_PROMPT
        )
        response = await agent.ainvoke({
        "messages": [{"role": "user", "content": 'HI'}]
                })
        print(response)
    
    # Run the async main function
    asyncio.run(main())
    
