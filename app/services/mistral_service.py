import os
import httpx
import hashlib
import asyncio
import random
from typing import Optional

MISTRAL_MODEL = "mistral-medium"
API_URL = "https://api.mistral.ai/v1/chat/completions"

def get_headers():
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        raise RuntimeError("MISTRAL_API_KEY not set in environment variables")
    return {"Authorization": f"Bearer {mistral_api_key}", "Content-Type": "application/json"}

async def post_chat(messages: list, max_retries: int = 3) -> str:
    """Post chat with retry logic and fallback responses"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {"model": MISTRAL_MODEL, "messages": messages}
                resp = await client.post(API_URL, json=payload, headers=get_headers())
                
                if resp.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff
                        print(f"Rate limited, waiting {wait_time:.2f}s before retry {attempt + 1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise httpx.HTTPStatusError("Rate limit exceeded", request=resp.request, response=resp)
                        
                resp.raise_for_status()
                j = resp.json()
                return j["choices"][0]["message"]["content"]
                
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"All attempts failed: {e}")
                raise e
            await asyncio.sleep(1)  # Brief wait before retry
    
    raise Exception("Unexpected error in post_chat")

def get_fallback_code_comment(code: str) -> str:
    """Fallback response when AI is unavailable"""
    lines = code.strip().split('\n')
    commented_lines = []
    for line in lines:
        if line.strip():
            commented_lines.append(f"# [AI unavailable] Code line: {line}")
            commented_lines.append(line)
        else:
            commented_lines.append(line)
    return '\n'.join(commented_lines)

async def comment_code_with_ai(code: str, language: Optional[str] = None) -> str:
    lang_note = f" (language: {language})" if language else ""
    prompt = f"Add clear, concise line-by-line comments to the following code{lang_note}. Keep comments short and useful:\n\n{code}"
    messages = [
        {"role": "system", "content": "You are a helpful code-commenting assistant."},
        {"role": "user", "content": prompt}
    ]
    try:
        return await post_chat(messages)
    except Exception as e:
        print(f"AI commenting failed, using fallback: {e}")
        return get_fallback_code_comment(code)

def get_fallback_daily_tip() -> str:
    """Fallback daily tips when AI is unavailable"""
    tips = [
        "💡 Always write clear variable names - future you will thank you!",
        "🧹 Clean code is not just about syntax, it's about expressing intent clearly.",
        "🔄 Refactor in small steps - big changes are hard to debug.",
        "📝 Comment the 'why', not the 'what' - your code shows what you're doing.",
        "🧪 Write tests first, then code - it helps clarify your thinking.",
        "⚡ Premature optimization is the root of all evil - make it work first.",
        "🔍 Use meaningful commit messages - they're documentation for your future self.",
        "🏗️ Build in small iterations - it's easier to spot problems early."
    ]
    import datetime
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return tips[day_of_year % len(tips)]

async def generate_daily_tip() -> str:
    seed = hashlib.sha256().hexdigest()[:6]
    prompt = f"Give one short, practical coding or engineering tip for developers. Include one emoji. Seed: {seed}"
    messages = [
        {"role": "system", "content": "You are a concise assistant that writes daily developer tips."},
        {"role": "user", "content": prompt}
    ]
    try:
        return await post_chat(messages)
    except Exception as e:
        print(f"AI tip generation failed, using fallback: {e}")
        return get_fallback_daily_tip()
