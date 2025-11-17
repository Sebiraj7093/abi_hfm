from fastapi import APIRouter, HTTPException
from app.models.request_models import OrchestrationRequest
from app.models.response_models import OrchestrationResponse
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/api/v1", tags=["Deep Agent"])

@router.post("/query", response_model=OrchestrationResponse)
async def query(request: OrchestrationRequest):
    """
    Unified query endpoint powered by Deep Agent.
    Automatically routes to SQL Agent or RAG Agent based on query type.
    """
    try:
        result = await OrchestrationService.handle_query(request.query)
        return OrchestrationResponse(
            success=result.get("success", False),
            response=result.get("response", result.get("data", "")),
            agent_used=result.get("agent")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
