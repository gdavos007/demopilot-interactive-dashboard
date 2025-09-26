from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.api.v1.voice import routes as voice_routes
from app.api.v1.knowledge import routes as knowledge_routes
from app.api.v1.evaluation import routes as evaluation_routes
from app.config.logging_config import setup_logging
from app.core.knowledge.agent import knowledge_agent

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    await knowledge_agent.initialize_agent()
    yield
    # Clean up the ML models and release the resources
    # (if needed)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    # Add your frontend ngrok URL here if you use one
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    voice_routes.router,
    prefix=f"{settings.API_V1_STR}/voice",
    tags=["voice"]
)

app.include_router(
    knowledge_routes.router,
    prefix=f"{settings.API_V1_STR}/knowledge",
    tags=["knowledge"]
)

app.include_router(
    evaluation_routes.router,
    prefix=f"{settings.API_V1_STR}/evaluation",
    tags=["evaluation"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DemoPilot API",
        "version": "0.1.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 