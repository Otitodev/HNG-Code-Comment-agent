from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.mistral_service import comment_code_with_ai
from app.services.language_detector import detect_language
from app.db import get_db
from app.models import CodeRequest as CodeRequestModel, UserLanguagePreference
from datetime import datetime

router = APIRouter(prefix="/api", tags=["comment"])

class CodeRequest(BaseModel):
    code: str

def get_user_id(request: Request) -> str:
    """Generate user ID from IP address (simple approach)"""
    return request.client.host if request.client else "unknown"

@router.post("/comment")
async def comment_code(req: CodeRequest, request: Request, db: AsyncSession = Depends(get_db)):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="code is empty")
    
    user_id = get_user_id(request)
    detected_language = detect_language(req.code)
    
    try:
        # Save the code request to database
        code_request = CodeRequestModel(
            user_id=user_id,
            code_snippet=req.code,
            detected_language=detected_language
        )
        db.add(code_request)
        
        # Update user's language preference if we detected a language
        if detected_language:
            # Check if user preference exists
            result = await db.execute(
                select(UserLanguagePreference).where(UserLanguagePreference.user_id == user_id)
            )
            user_pref = result.scalar_one_or_none()
            
            if user_pref:
                user_pref.primary_language = detected_language
                user_pref.last_updated = datetime.utcnow()
            else:
                user_pref = UserLanguagePreference(
                    user_id=user_id,
                    primary_language=detected_language
                )
                db.add(user_pref)
        
        await db.commit()
        
        # Generate commented code
        commented = await comment_code_with_ai(req.code, detected_language)
        
        return {
            "commented_code": commented,
            "detected_language": detected_language,
            "user_id": user_id
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
