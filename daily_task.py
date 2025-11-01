#!/usr/bin/env python3
"""
Daily Task Automation for Code Commenter Agent

This script generates and stores daily coding tips in the database.
It can be run manually or scheduled via cron/GitHub Actions.
"""

import os
import asyncio
import httpx
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
SUPPORTED_LANGUAGES = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", 
    "rust", "php", "ruby", "swift", "kotlin", "sql"
]

async def generate_daily_tips():
    """Generate daily tips for all supported languages"""
    print(f"🚀 Starting daily tips generation for {date.today()}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Generate general daily tip
        try:
            print("📝 Generating general daily tip...")
            response = await client.get(f"{API_BASE_URL}/api/daily-tip")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ General tip: {result['tip'][:50]}...")
            else:
                print(f"❌ Failed to generate general tip: {response.status_code}")
        except Exception as e:
            print(f"❌ Error generating general tip: {e}")
        
        # Generate language-specific tips
        for language in SUPPORTED_LANGUAGES:
            try:
                print(f"📝 Generating {language} tip...")
                
                # Make a request that would trigger language-specific tip generation
                # We'll simulate a user with that language preference
                response = await client.get(
                    f"{API_BASE_URL}/api/daily-tip",
                    headers={"X-User-Language": language}  # Custom header for testing
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('language') == language:
                        print(f"✅ {language} tip: {result['tip'][:50]}...")
                    else:
                        print(f"⚠️  {language} tip generated as general tip")
                else:
                    print(f"❌ Failed to generate {language} tip: {response.status_code}")
                    
                # Small delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error generating {language} tip: {e}")

async def test_api_health():
    """Test if the API is healthy before generating tips"""
    print("🔍 Checking API health...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_BASE_URL}/ping")
            if response.status_code == 200:
                print("✅ API is healthy")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

async def send_notification(message: str):
    """Send notification about daily tips generation (placeholder)"""
    print(f"📢 Notification: {message}")
    # Here you could integrate with Slack, Discord, email, etc.

async def main():
    """Main function to run daily tasks"""
    print("=" * 60)
    print("🤖 Code Commenter Agent - Daily Tasks")
    print(f"📅 Date: {date.today()}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Check API health first
    if not await test_api_health():
        await send_notification("❌ Daily tips generation failed - API not healthy")
        return
    
    # Generate daily tips
    try:
        await generate_daily_tips()
        await send_notification("✅ Daily tips generation completed successfully")
        print("\n🎉 Daily tasks completed successfully!")
        
    except Exception as e:
        error_msg = f"❌ Daily tips generation failed: {e}"
        await send_notification(error_msg)
        print(f"\n{error_msg}")
        raise

if __name__ == "__main__":
    asyncio.run(main())