from pydantic import BaseModel
from typing import Any, Optional

class SQLQueryResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    
class RAGQueryResponse(BaseModel):
    success: bool
    answer: str
    
class OrchestrationResponse(BaseModel):
    success: bool
    response: str
    agent_used: Optional[str] = None
