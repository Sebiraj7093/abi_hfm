from pydantic import BaseModel, Field

class SQLQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    
class RAGQueryRequest(BaseModel):
    question: str = Field(..., description="Question for knowledge base")
    
class OrchestrationRequest(BaseModel):
    query: str = Field(..., description="User query")
