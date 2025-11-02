import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Now import other modules that depend on environment variables
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.db import Base, engine
from app.routes import comment, daily_tip, telex_webhook

app = FastAPI(
    title="Telex AI Agent",
    description="AI Agent for Telex.im integration with intelligent chat assistance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    try:
        # Test database connection
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables verified")
        
    except Exception as e:
        logger.error(f"⚠️  Database connection failed: {e}")
        logger.info("App will run but some endpoints may not work")

# Include routers
app.include_router(telex_webhook.router)
app.include_router(comment.router)
app.include_router(daily_tip.router)

@app.get("/")
async def root():
    """Welcome route with API information"""
    return {
        "message": "Multi-Purpose AI Agent",
        "version": "1.0.0",
        "description": "Code Commenter Agent + Telex.im AI Assistant",
        "features": {
            "code_commenting": "Add intelligent comments to code snippets",
            "daily_tips": "Personalized coding tips and best practices",
            "telex_integration": "AI chat assistance via Telex.im",
            "language_detection": "Support for 15+ programming languages"
        },
        "endpoints": {
            "health": "/ping",
            "code_comment": "/api/comment",
            "daily_tip": "/api/daily-tip",
            "user_stats": "/api/user-stats",
            "telex_webhook": "/webhook",
            "ai_respond": "/respond",
            "docs": "/docs"
        }
    }

@app.get("/ping")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Telex AI Agent is operational"
    }

@app.get("/kaithheathcheck")
async def leapcell_health_check():
    """Leapcell health check endpoint"""
    return {"status": "ok"}

@app.get("/kaithhealthcheck")
async def leapcell_health_check_alt():
    """Alternative Leapcell health check endpoint"""
    return {"status": "ok"}
