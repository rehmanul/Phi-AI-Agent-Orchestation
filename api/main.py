"""
FastAPI Application

Main API server for the advocacy orchestration system.
Provides REST and GraphQL endpoints for the dashboard.
"""

from contextlib import asynccontextmanager
from typing import List

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import campaigns, content, intelligence, legislators, metrics, agents, settings
from core.config import settings as app_settings
from core.database import async_engine, get_async_session
from core.messaging import shutdown_producer

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting API server")
    
    # Startup - initialize default settings
    try:
        async for session in get_async_session():
            from api.routes.settings import initialize_default_settings
            await initialize_default_settings(session)
            break
    except Exception as e:
        logger.warning("Could not initialize default settings", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server")
    await shutdown_producer()
    await async_engine.dispose()


app = FastAPI(
    title="Advocacy Orchestration API",
    description="Multi-agent AI system for grassroots lobbying campaigns",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(legislators.router, prefix="/api/legislators", tags=["Legislators"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(settings.router, prefix="/api", tags=["Settings"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Advocacy Orchestration API",
        "version": "1.0.0",
        "docs": "/docs",
        "graphql": "/graphql",
    }
