"""
FastAPI Application Factory and Configuration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from api.routers import (
    auth_router, users_router, machines_router, 
    worksheets_router, assets_router, permissions_router
)
from api.routers.health import router as health_router
# Inventory, PM, Reports router-ek később hozzáadhatók, ha szükséges
from api.routers.inventory import router as inventory_router
from api.routers.pm import router as pm_router
from api.routers.reports import router as reports_router
import logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title="CMMS REST API",
        description="Computerized Maintenance Management System REST API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:3000",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "*"  # For development only; restrict in production
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(machines_router, prefix="/api")
    app.include_router(worksheets_router, prefix="/api")
    app.include_router(assets_router, prefix="/api")
    app.include_router(permissions_router, prefix="/api")
    # Inventory, PM, Reports router-ek később hozzáadhatók
    app.include_router(inventory_router, prefix="/api")
    app.include_router(pm_router, prefix="/api")
    app.include_router(reports_router, prefix="/api")
    
    # Root endpoint
    @app.get("/")
    async def root():
        """API root endpoint"""
        return {
            "message": "CMMS REST API",
            "docs": "/api/docs",
            "redoc": "/api/redoc"
        }
    
    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title="CMMS REST API",
            version="1.0.0",
            description="Computerized Maintenance Management System REST API",
            routes=app.routes,
        )
        
        # Add security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        
        # Add global security requirement
        openapi_schema["security"] = [{"bearerAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    logger.info("FastAPI application created successfully")
    return app
