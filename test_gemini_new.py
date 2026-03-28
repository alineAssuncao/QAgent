from google import genai
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return
    
    client = genai.Client(api_key=api_key)
    try:
        # Test synchronous call first if it's simpler, or check for .aio
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Olá, diga 'Oi' se estiver funcionando."
        )
        print(f"Sync Response: {response.text}")
    except Exception as e:
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
