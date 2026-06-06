from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn
import os

from core.database import init_db, get_db
from core.config import settings
from core.middleware import get_current_tenant
from api import auth
from models.database import Tenant

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing SaaS platform...")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Portfolio AI SaaS",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Routes
app.include_router(auth.router)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/dashboard")
async def dashboard(
    tenant: Tenant = Depends(get_current_tenant),
    db = Depends(get_db)
):
    """Get tenant dashboard data"""
    return {
        "tenant_name": tenant.name,
        "tier": tenant.tier,
        "usage_this_month": {
            "tokens": 0,
            "sessions": 0,
            "percentage_of_limit": 0
        },
        "next_billing_date": "2026-07-06"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
