# Purpose: Create the FastAPI application, register routes, and manage startup/shutdown resources.
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS, PINNED_VERSIONS
from app.database import init_db
from app.jobs import recover_interrupted_jobs
from app.routes import scans, patches, demo, reviews, dashboard
from app.tooling import toolchain_status

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite database tables and recover any interrupted jobs
    init_db()
    recover_interrupted_jobs()
    yield
    # Shutdown

app = FastAPI(
    title="Fusion Security Workbench API",
    description="Local Solidity security workbench: Slither static analysis, reviewable patches, and local EVM attack/defense evidence.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS restricted to local frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(scans.router)
app.include_router(patches.router)
app.include_router(demo.router)
app.include_router(reviews.router)
app.include_router(dashboard.router)

@app.get("/api/health")
def health_check():
    status = toolchain_status()
    ready = bool(status["available"])
    return {
        "status": "healthy" if ready else "degraded",  # liveness vs readiness: degraded when tools missing
        "ready": ready,
        "service": "Fusion Security Workbench",
        "tool_versions": status["observed"],
        "toolchain": status,
    }

@app.get("/api/capabilities")
def capabilities():
    status = toolchain_status()
    from app.config import (
        ARBITRARY_SCAN_ISOLATION_ENABLED,
        ANALYSIS_TIMEOUT_SECONDS,
        MAX_UPLOAD_SIZE,
        ANVIL_CHAIN_ID,
        ANVIL_RPC_URL,
    )
    return {
        "ready": bool(status["available"]),
        "expected_tool_versions": status["expected"],
        "observed_tool_versions": status["observed"],
        "worker_mode": "curated-only",
        "worker_reason": "verified isolated worker not yet validated (P02)",
        "arbitrary_upload_available": bool(ARBITRARY_SCAN_ISOLATION_ENABLED),
        "max_upload_bytes": MAX_UPLOAD_SIZE,
        "analysis_timeout_seconds": ANALYSIS_TIMEOUT_SECONDS,
        "chain": {"rpc_url": ANVIL_RPC_URL, "chain_id": ANVIL_CHAIN_ID},
        "checked_at": status.get("checked_at"),
    }
