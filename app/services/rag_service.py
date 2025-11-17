"""RAG Service - Wrapper for RAG Agent"""
import sys
sys.path.insert(0, '/home/avivekanandan/SQL_Agent')

from RAG_Agent import RAGAgent, load_csv_files

class RAGService:
    _agent = None
    _initialized = False
    
    @classmethod
    async def initialize(cls, google_api_key: str, pgvector_connection: str):
        if cls._initialized:
            return
        
        cls._agent = RAGAgent()
        await cls._agent.initialize()
        await load_csv_files(cls._agent)
        cls._initialized = True
    
    @classmethod
    async def query(cls, question: str) -> str:
        if not cls._initialized:
            return "RAG service not initialized"
        return await cls._agent.query(question)
    
    @classmethod
    async def health_check(cls) -> bool:
        return cls._initialized
