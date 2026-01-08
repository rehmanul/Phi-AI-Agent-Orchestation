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

from api.routes import campaigns, content, intelligence, legislators, metrics, agents
from core.config import settings
from core.database import async_engine
from core.messaging import shutdown_producer

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting API server")
    
    # Startup
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
    allow_origins=settings.cors_origins,
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
