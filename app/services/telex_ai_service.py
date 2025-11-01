import logging
import json
from typing import Dict, Any, Optional
from app.services.mistral_service import MistralService

logger = logging.getLogger(__name__)

class TelexAIService:
    """
    Service for processing Telex messages and generating AI responses
    """
    
    def __init__(self, mistral_service: MistralService):
        self.mistral_service = mistral_service
        
    async def process_message(
        self, 
        message: str, 
        user: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate appropriate response
        
        Args:
            message: The user's message
            user: Username
            context: Additional context (channel_id, timestamp, etc.)
            
        Returns:
            Dict containing the response in Telex format
        """
        try:
            logger.info(f"Processing message from {user}: {message[:50]}...")
            
            # Determine the type of assistance needed
            response_type = self._classify_message(message)
            
            if response_type == "code_help":
                ai_response = await self._handle_code_assistance(message, user, context)
            elif response_type == "general_chat":
                ai_response = await self._handle_general_chat(message, user, context)
            elif response_type == "summarization":
                ai_response = await self._handle_summarization(message, user, context)
            else:
                ai_response = await self._handle_default(message, user, context)
            
            # Format response for Telex
            telex_response = self._format_telex_response(ai_response, user)
            
            logger.info(f"Generated response for {user}")
            return telex_response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return self._format_error_response(str(e))
    
    def _classify_message(self, message: str) -> str:
        """
        Classify the type of message to determine appropriate handling
        """
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in [
            "code", "function", "bug", "error", "debug", "programming", 
            "python", "javascript", "java", "c++", "sql"
        ]):
            return "code_help"
        elif any(keyword in message_lower for keyword in [
            "summarize", "summary", "tldr", "brief", "overview"
        ]):
            return "summarization"
        elif any(keyword in message_lower for keyword in [
            "hello", "hi", "help", "what can you do", "how are you"
        ]):
            return "general_chat"
        else:
            return "default"
    
    async def _handle_code_assistance(
        self, 
        message: str, 
        user: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Handle code-related queries"""
        prompt = f"""You are a helpful coding assistant. The user {user} has asked: "{message}"

Please provide a clear, helpful response that:
1. Addresses their specific coding question
2. Provides code examples if relevant
3. Explains the solution step by step
4. Suggests best practices

Keep your response concise but comprehensive."""

        try:
            response = await self.mistral_service.generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error in code assistance: {str(e)}")
            return "I'm having trouble processing your code question right now due to high demand. Please try again in a moment."
    
    async def _handle_general_chat(
        self, 
        message: str, 
        user: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Handle general chat and greetings"""
        prompt = f"""You are a friendly AI assistant integrated with Telex.im. The user {user} said: "{message}"

Respond in a helpful, conversational way. If they're greeting you or asking what you can do, explain that you're an AI assistant that can help with:
- Code review and programming questions
- Text summarization
- General questions and conversation
- Technical assistance

Keep your response warm and engaging."""

        try:
            response = await self.mistral_service.generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error in general chat: {str(e)}")
            return f"Hello {user}! I'm your AI assistant, though I'm experiencing some technical difficulties right now. I can help with coding questions, summarization, and general assistance. Please try again in a moment!"
    
    async def _handle_summarization(
        self, 
        message: str, 
        user: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Handle summarization requests"""
        prompt = f"""The user {user} has requested summarization: "{message}"

Please provide a clear, concise summary of the content they've shared. Focus on:
1. Key points and main ideas
2. Important details
3. Actionable items if any
4. Clear structure

If they haven't provided content to summarize, ask them to share the content they'd like summarized."""

        try:
            response = await self.mistral_service.generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            return "I'd be happy to help summarize content for you. Please share the text or document you'd like me to summarize."
    
    async def _handle_default(
        self, 
        message: str, 
        user: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Handle default/unclassified messages"""
        prompt = f"""The user {user} sent: "{message}"

Please provide a helpful response. Try to understand what they need and offer appropriate assistance. You can help with coding, summarization, general questions, and more."""

        try:
            response = await self.mistral_service.generate_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error in default handling: {str(e)}")
            return "I'm here to help! I can assist with coding questions, summarization, and general inquiries. What would you like to know?"
    
    def _format_telex_response(self, ai_response: str, user: str) -> Dict[str, Any]:
        """
        Format AI response into Telex-compliant JSON structure
        """
        return {
            "message": ai_response,
            "action": "reply",
            "metadata": {
                "user": user,
                "agent": "telex-ai-assistant",
                "response_type": "ai_generated"
            }
        }
    
    def _format_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Format error response for Telex
        """
        return {
            "message": "I'm experiencing some technical difficulties. Please try again in a moment.",
            "action": "reply",
            "metadata": {
                "agent": "telex-ai-assistant",
                "response_type": "error",
                "error": error_message
            }
        }


