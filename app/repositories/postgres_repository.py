import asyncpg
from typing import List, Dict, Any, Optional

class PostgresRepository:
    _pool: Optional[asyncpg.Pool] = None
    
    @classmethod
    async def initialize(cls, db_config: Dict[str, Any]):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(**db_config, min_size=5, max_size=20)
    
    @classmethod
    async def execute_query(cls, sql: str) -> List[Dict[str, Any]]:
        async with cls._pool.acquire() as conn:
            results = await conn.fetch(sql)
            return [dict(row) for row in results]
    
    @classmethod
    async def fetch_schema(cls, table_name: str) -> str:
        async with cls._pool.acquire() as conn:
            results = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = $1
            """, table_name)
            return "\n".join(f"{r['column_name']}: {r['data_type']}" for r in results)
    
    @classmethod
    async def cleanup(cls):
        if cls._pool:
            await cls._pool.close()
    
    @classmethod
    async def health_check(cls) -> bool:
        try:
            async with cls._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except:
            return False
