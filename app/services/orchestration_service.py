"""Orchestration Service - Wrapper for Orchestration"""
import sys
sys.path.insert(0, '/home/avivekanandan/SQL_Agent')

from orchestration import orchestration_handle, initialize_orchestration, cleanup_orchestration

class OrchestrationService:
    _initialized = False
    
    @classmethod
    async def initialize(cls):
        if cls._initialized:
            return
        await initialize_orchestration()
        cls._initialized = True
    
    @classmethod
    async def handle_query(cls, user_query: str) -> dict:
        if not cls._initialized:
            await cls.initialize()
        
        response = await orchestration_handle(user_query)
        return {"success": True, "response": response, "agent": "orchestration"}
    
    @classmethod
    async def cleanup(cls):
        await cleanup_orchestration()
