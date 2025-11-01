from typing import Optional
from supabase import create_client, Client
from ..config import config

class SupabaseService:
    """Service for interacting with Supabase beyond just the database"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        if config.SUPABASE_URL and config.SUPABASE_ANON_KEY:
            self.client = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        return self.client
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes) -> dict:
        """Upload a file to Supabase Storage"""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        response = self.client.storage.from_(bucket).upload(file_path, file_data)
        return response
    
    async def get_file_url(self, bucket: str, file_path: str) -> str:
        """Get a public URL for a file in Supabase Storage"""
        if not self.client:
            raise ValueError("Supabase client not initialized")
        
        response = self.client.storage.from_(bucket).get_public_url(file_path)
        return response
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self.client is not None

# Global instance
supabase_service = SupabaseService()