from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.mistral_service import comment_code_with_ai

router = APIRouter(prefix="/api", tags=["comment"])

class CodeRequest(BaseModel):
    code: str

@router.post("/comment")
async def comment_code(req: CodeRequest):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="code is empty")
    try:
        commented = await comment_code_with_ai(req.code)
        return {"commented_code": commented}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
