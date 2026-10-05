"""Nifty 100 Financial Intelligence Platform - FastAPI Application.

Sprint 6:
- Day 38: FastAPI server scaffold
- Day 39: Company API routes
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes.companies import router as companies_router

from src.api.routes.analytics import router as analytics_router

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "nifty100.db"

API_VERSION = "1.0.0"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Nifty 100 Financial Intelligence API",
    description=(
        "REST API for the Nifty 100 Financial Intelligence "
        "Platform."
    ),
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DAY 39 ROUTERS
# ============================================================

app.include_router(companies_router)
app.include_router(analytics_router)

# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database() -> dict:
    """Verify SQLite connectivity and company-table availability."""

    if not DATABASE_PATH.exists():

        return {
            "status": "unavailable",
            "connected": False,
            "database": str(DATABASE_PATH),
            "companies": None,
            "message": "Database file not found.",
        }

    try:

        with sqlite3.connect(
            DATABASE_PATH
        ) as connection:

            company_count = int(
                connection.execute(
                    "SELECT COUNT(*) FROM companies"
                ).fetchone()[0]
            )

        return {
            "status": "healthy",
            "connected": True,
            "database": str(DATABASE_PATH),
            "companies": company_count,
            "message": (
                "SQLite database connection successful."
            ),
        }

    except sqlite3.Error as exc:

        return {
            "status": "unavailable",
            "connected": False,
            "database": str(DATABASE_PATH),
            "companies": None,
            "message": str(exc),
        }


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
def root():
    """Return API identification information."""

    return {
        "application": (
            "Nifty 100 Financial Intelligence Platform"
        ),
        "service": "Financial Intelligence REST API",
        "version": API_VERSION,
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get(
    "/health",
    tags=["System"],
)
def health():
    """Return API and database health."""

    database = check_database()

    return {
        "status": (
            "healthy"
            if database["connected"]
            else "degraded"
        ),
        "api": "healthy",
        "version": API_VERSION,
        "database": database,
    }


# ============================================================
# GLOBAL ERROR HANDLER
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """Return consistent JSON for unexpected server errors."""

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "Internal Server Error",
            "path": request.url.path,
            "detail": str(exc),
        },
    )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )