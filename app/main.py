import importlib
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.configuration import APPLICATION_NAME, ROOT, GOOGLE_API_KEY, DB_CONFIG, PGVECTOR_CONNECTION
from app.services.sql_service import SQLService
from app.services.rag_service import RAGService
from app.services.orchestration_service import OrchestrationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    await SQLService.initialize(GOOGLE_API_KEY, DB_CONFIG)
    await RAGService.initialize(GOOGLE_API_KEY, PGVECTOR_CONNECTION)
    await OrchestrationService.initialize()
    yield
    await SQLService.cleanup()

app = FastAPI(
    title=APPLICATION_NAME,
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=f"{ROOT}/static"), name="static")

# Load routers
for filename in os.listdir(f"{ROOT}/endpoints"):
    if filename.endswith(".py") and filename != "__init__.py":
        module = importlib.import_module(f"app.endpoints.{filename[:-3]}")
        if hasattr(module, 'router'):
            app.include_router(module.router)
