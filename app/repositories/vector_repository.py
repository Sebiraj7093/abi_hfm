import psycopg2
from typing import List, Dict, Any, Optional

class VectorRepository:
    _connection_string: Optional[str] = None
    
    @classmethod
    def initialize(cls, connection_string: str):
        cls._connection_string = connection_string
    
    @classmethod
    async def health_check(cls) -> bool:
        try:
            conn = psycopg2.connect(cls._connection_string)
            conn.close()
            return True
        except:
            return False
