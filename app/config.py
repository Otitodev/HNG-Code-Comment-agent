import os
from typing import Optional

class Config:
    """Configuration class for environment variables"""
    
    # AI Service Configuration
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")
    
    # Telex Configuration
    TELEX_AGENT_API_KEY: Optional[str] = os.getenv("TELEX_AGENT_API_KEY")
    TELEX_WEBHOOK_SECRET: Optional[str] = os.getenv("TELEX_WEBHOOK_SECRET")
    
    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # API Configuration
    API_BASE_URL: Optional[str] = os.getenv("API_BASE_URL", "")
    
    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_required_vars(cls) -> bool:
        """Validate that required environment variables are set"""
        required_vars = ["MISTRAL_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True

# Global config instance
config = Config()