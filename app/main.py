import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Now import other modules that depend on environment variables
from fastapi import FastAPI
from app.db import Base, engine
from app.routes import comment, daily_tip

app = FastAPI(title="Code Commenter Agent (Async)")

@app.on_event("startup")
async def startup_event():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("App will run but daily-tip endpoint may not work")

app.include_router(comment.router)
app.include_router(daily_tip.router)

@app.get("/")
async def root():
    return {"message": "Code Commenter Agent (Async) is running"}
