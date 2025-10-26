from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.db import get_db
from app.models import DailyTip
from app.services.mistral_service import generate_daily_tip

router = APIRouter(prefix="/api", tags=["daily-tip"])

# In-memory cache for when database is unavailable
_daily_tips_cache = {}

@router.get("/daily-tip")
async def daily_tip(db: AsyncSession = Depends(get_db)):
    today = date.today()
    
    # Try database first
    try:
        result = await db.execute(select(DailyTip).where(DailyTip.date == today))
        tip_row = result.scalar_one_or_none()

        if tip_row:
            return {"tip": tip_row.tip, "date": str(today), "source": "database"}

        # Generate new tip and save to database
        tip_text = await generate_daily_tip()
        new = DailyTip(date=today, tip=tip_text)
        db.add(new)
        await db.commit()
        return {"tip": tip_text, "date": str(today), "source": "database"}
        
    except Exception as db_error:
        print(f"Database error: {db_error}")
        
        # Check in-memory cache
        today_str = str(today)
        if today_str in _daily_tips_cache:
            return {"tip": _daily_tips_cache[today_str], "date": today_str, "source": "cache"}
        
        # Generate new tip and cache it
        try:
            tip_text = await generate_daily_tip()
            _daily_tips_cache[today_str] = tip_text
            return {"tip": tip_text, "date": today_str, "source": "cache"}
        except Exception as tip_error:
            raise HTTPException(status_code=500, detail=f"Database and AI both failed: {db_error}, {tip_error}")
