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

async def generate_language_specific_tip(language: str) -> str:
    """Generate a daily tip specific to a programming language"""
    from app.services.language_detector import get_language_specific_tip_prompt
    
    seed = hashlib.sha256(language.encode()).hexdigest()[:6]
    prompt = get_language_specific_tip_prompt(language) + f" Seed: {seed}"
    
    messages = [
        {"role": "system", "content": f"You are a concise assistant that writes daily tips for {language} developers. Be specific and practical."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        return await post_chat(messages)
    except Exception as e:
        print(f"AI language-specific tip generation failed, using fallback: {e}")
        return get_fallback_language_tip(language)

def get_fallback_language_tip(language: str) -> str:
    """Fallback language-specific tips when AI is unavailable"""
    language_tips = {
        'python': [
            "🐍 Use list comprehensions for cleaner, more Pythonic code: `[x*2 for x in range(10)]`",
            "📦 Use virtual environments to isolate project dependencies: `python -m venv myenv`",
            "🔍 Use f-strings for readable string formatting: `f'Hello {name}!'`",
            "⚡ Use `enumerate()` instead of manual counters: `for i, item in enumerate(items):`"
        ],
        'javascript': [
            "🚀 Use arrow functions for cleaner syntax: `const add = (a, b) => a + b`",
            "📋 Use destructuring for cleaner object access: `const {name, age} = person`",
            "🔄 Use `async/await` instead of promise chains for better readability",
            "🎯 Use `const` by default, `let` when reassigning, avoid `var`"
        ],
        'java': [
            "☕ Use StringBuilder for multiple string concatenations instead of + operator",
            "🏗️ Follow naming conventions: classes PascalCase, methods camelCase",
            "🔒 Make fields private and use getters/setters for encapsulation",
            "📚 Use ArrayList instead of Vector for better performance"
        ],
        'typescript': [
            "🎯 Use strict type checking: enable `strict: true` in tsconfig.json",
            "🔧 Define interfaces for object shapes: `interface User { name: string; age: number; }`",
            "⚡ Use union types for flexible parameters: `string | number`",
            "🛡️ Use optional chaining: `user?.profile?.email` for safe property access"
        ]
    }
    
    tips = language_tips.get(language, [
        f"💡 Write clean, readable {language} code with meaningful variable names!",
        f"🧪 Test your {language} code thoroughly before deployment!",
        f"📝 Comment complex {language} logic for future maintainers!"
    ])
    
    import datetime
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    return tips[day_of_year % len(tips)]

class MistralService:
    """
    Service class for Mistral AI interactions
    """
    
    def __init__(self):
        self.model = MISTRAL_MODEL
        self.api_url = API_URL
    
    async def generate_response(self, prompt: str, system_message: str = None) -> str:
        """
        Generate a response using Mistral AI
        
        Args:
            prompt: The user prompt
            system_message: Optional system message to set context
            
        Returns:
            Generated response string
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        else:
            messages.append({"role": "system", "content": "You are a helpful AI assistant."})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            return await post_chat(messages)
        except Exception as e:
            print(f"Mistral API error: {e}")
            return "I'm having trouble generating a response right now. Please try again later."
