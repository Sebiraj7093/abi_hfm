from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.configuration import ROOT

router = APIRouter(tags=["UI"])

@router.get("/")
async def serve_ui():
    return FileResponse(f"{ROOT}/static/index.html")