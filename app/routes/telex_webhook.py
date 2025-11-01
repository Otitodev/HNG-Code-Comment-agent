import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from app.services.telex_ai_service import TelexAIService
from app.services.mistral_service import MistralService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["telex"])

# Pydantic models for request/response
class TelexMessageData(BaseModel):
    user: str = Field(..., description="Username who sent the message")
    message: str = Field(..., description="Message content")
    channel_id: Optional[str] = Field(None, description="Channel ID if applicable")
    timestamp: Optional[str] = Field(None, description="Message timestamp")

class TelexWebhookPayload(BaseModel):
    event: str = Field(..., description="Event type (e.g., message_received)")
    data: TelexMessageData = Field(..., description="Event data")

class TelexResponse(BaseModel):
    response: Dict[str, Any] = Field(..., description="Response data for Telex")

class AIProcessRequest(BaseModel):
    message: str = Field(..., description="Message to process")
    user: Optional[str] = Field(None, description="User context")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

# Dependency to get AI service
def get_ai_service() -> TelexAIService:
    mistral_service = MistralService()
    return TelexAIService(mistral_service)

@router.post("/webhook", response_model=TelexResponse)
async def telex_webhook(
    payload: TelexWebhookPayload,
    request: Request,
    ai_service: TelexAIService = Depends(get_ai_service)
):
    """
    Main Telex event handler - receives messages/events from Telex.im
    """
    try:
        logger.info(f"Received webhook event: {payload.event} from user: {payload.data.user}")
        
        # Process the message based on event type
        if payload.event == "message_received":
            response_data = await ai_service.process_message(
                message=payload.data.message,
                user=payload.data.user,
                context={
                    "channel_id": payload.data.channel_id,
                    "timestamp": payload.data.timestamp
                }
            )
            
            logger.info(f"Generated response for user {payload.data.user}")
            return TelexResponse(response=response_data)
        
        else:
            # Handle other event types or return a default response
            logger.warning(f"Unhandled event type: {payload.event}")
            return TelexResponse(response={
                "message": f"Event '{payload.event}' received but not processed",
                "action": "acknowledge"
            })
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/respond", response_model=Dict[str, Any])
async def ai_respond(
    request: AIProcessRequest,
    ai_service: TelexAIService = Depends(get_ai_service)
):
    """
    Internal AI processing route for testing and direct API access
    """
    try:
        logger.info(f"Processing AI request from user: {request.user}")
        
        response_data = await ai_service.process_message(
            message=request.message,
            user=request.user or "anonymous",
            context=request.context or {}
        )
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in AI processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {str(e)}"
        )

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint to verify the webhook is working
    """
    return {
        "status": "success",
        "message": "Telex webhook endpoint is operational",
        "timestamp": "2024-01-01T00:00:00Z"
    }