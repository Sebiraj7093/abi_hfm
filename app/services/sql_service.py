"""SQL Service - Wrapper for SQL Agent"""
import sys
sys.path.insert(0, '/home/avivekanandan/SQL_Agent')

from SQL_Agent import agent as sql_agent, init_db_pool, cleanup_db_pool

class SQLService:
    _initialized = False
    
    @classmethod
    async def initialize(cls, google_api_key: str, db_config: dict):
        if cls._initialized:
            return
        await init_db_pool()
        cls._initialized = True
    
    @classmethod
    async def execute_query(cls, user_query: str) -> dict:
        try:
            response = await sql_agent.ainvoke({
                "messages": [{"role": "user", "content": user_query}]
            })
            
            messages = response.get("messages", [])
            for message in reversed(messages):
                if hasattr(message, 'content') and message.content:
                    return {"success": True, "data": message.content}
            
            return {"success": False, "data": "No response"}
        except Exception as e:
            return {"success": False, "data": str(e)}
    
    @classmethod
    async def cleanup(cls):
        await cleanup_db_pool()
    
    @classmethod
    async def health_check(cls) -> bool:
        return cls._initialized
