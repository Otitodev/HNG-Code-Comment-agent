from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.db import get_db
from app.models import DailyTip, UserLanguagePreference, CodeRequest as CodeRequestModel
from app.services.mistral_service import generate_daily_tip, generate_language_specific_tip

router = APIRouter(prefix="/api", tags=["daily-tip"])

# In-memory cache for when database is unavailable
_daily_tips_cache = {}

def get_user_id(request: Request) -> str:
    """Generate user ID from IP address (simple approach)"""
    return request.client.host if request.client else "unknown"

@router.get("/daily-tip")
async def daily_tip(request: Request, db: AsyncSession = Depends(get_db)):
    today = date.today()
    user_id = get_user_id(request)
    
    # Try to get user's preferred language
    user_language = None
    try:
        # First check user preferences
        result = await db.execute(
            select(UserLanguagePreference).where(UserLanguagePreference.user_id == user_id)
        )
        user_pref = result.scalar_one_or_none()
        
        if user_pref:
            user_language = user_pref.primary_language
        else:
            # Fallback: get most recent language from user's code requests
            result = await db.execute(
                select(CodeRequestModel.detected_language)
                .where(CodeRequestModel.user_id == user_id)
                .where(CodeRequestModel.detected_language.isnot(None))
                .order_by(desc(CodeRequestModel.created_at))
                .limit(1)
            )
            recent_language = result.scalar_one_or_none()
            if recent_language:
                user_language = recent_language
    except Exception as e:
        print(f"Error getting user language preference: {e}")
    
    # Create cache key that includes language
    cache_key = f"{today}_{user_language or 'general'}"
    
    # Try database first
    try:
        result = await db.execute(
            select(DailyTip).where(
                DailyTip.date == today,
                DailyTip.language == user_language
            )
        )
        tip_row = result.scalar_one_or_none()

        if tip_row:
            return {
                "tip": tip_row.tip, 
                "date": str(today), 
                "source": "database",
                "language": user_language,
                "personalized": user_language is not None
            }

        # Generate new tip and save to database
        if user_language:
            tip_text = await generate_language_specific_tip(user_language)
        else:
            tip_text = await generate_daily_tip()
            
        new = DailyTip(date=today, tip=tip_text, language=user_language)
        db.add(new)
        await db.commit()
        
        return {
            "tip": tip_text, 
            "date": str(today), 
            "source": "database",
            "language": user_language,
            "personalized": user_language is not None
        }
        
    except Exception as db_error:
        print(f"Database error: {db_error}")
        
        # Check in-memory cache
        if cache_key in _daily_tips_cache:
            return {
                "tip": _daily_tips_cache[cache_key], 
                "date": str(today), 
                "source": "cache",
                "language": user_language,
                "personalized": user_language is not None
            }
        
        # Generate new tip and cache it
        try:
            if user_language:
                tip_text = await generate_language_specific_tip(user_language)
            else:
                tip_text = await generate_daily_tip()
                
            _daily_tips_cache[cache_key] = tip_text
            return {
                "tip": tip_text, 
                "date": str(today), 
                "source": "cache",
                "language": user_language,
                "personalized": user_language is not None
            }
        except Exception as tip_error:
            raise HTTPException(status_code=500, detail=f"Database and AI both failed: {db_error}, {tip_error}")

@router.get("/user-stats")
async def get_user_stats(request: Request, db: AsyncSession = Depends(get_db)):
    """Get user's coding activity stats"""
    user_id = get_user_id(request)
    
    try:
        # Get user's language preference
        pref_result = await db.execute(
            select(UserLanguagePreference).where(UserLanguagePreference.user_id == user_id)
        )
        user_pref = pref_result.scalar_one_or_none()
        
        # Get recent code requests
        requests_result = await db.execute(
            select(CodeRequestModel.detected_language)
            .where(CodeRequestModel.user_id == user_id)
            .order_by(desc(CodeRequestModel.created_at))
            .limit(10)
        )
        recent_languages = [row[0] for row in requests_result.fetchall() if row[0]]
        
        # Count language usage
        language_counts = {}
        for lang in recent_languages:
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            "user_id": user_id,
            "primary_language": user_pref.primary_language if user_pref else None,
            "recent_languages": recent_languages,
            "language_usage": language_counts,
            "total_requests": len(recent_languages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
