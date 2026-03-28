import logging
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.config import settings
import google.generativeai as genai
from openai import AsyncOpenAI

class BaseProvider(ABC):
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

class LMStudioProvider(BaseProvider):
    def __init__(self, base_url: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key="lm-studio")
        self.base_url = base_url

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models", timeout=2.0)
                return response.status_code == 200
        except Exception:
            return False

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        response = await self.client.chat.completions.create(
            model="local-model",
            messages=messages
        )
        return response.choices[0].message.content

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # Simplificando a conversão de formato de mensagens para o Gemini
        chat = self.model.start_chat(history=[])
        prompt = messages[-1]['content']
        response = chat.send_message(prompt)
        return response.text

class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str = None, name: str = "OpenAI"):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.name = name
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo" if "openai" in self.name.lower() else "deepseek-chat",
            messages=messages
        )
        return response.choices[0].message.content

class ProviderFactory:
    @staticmethod
    async def get_active_provider() -> BaseProvider:
        # 1. Tentar LM Studio (Prioridade Local)
        lm_studio = LMStudioProvider(settings.LM_STUDIO_BASE_URL)
        if await lm_studio.is_available():
            logging.info("Utilizando Provedor: LM Studio (Local)")
            return lm_studio

        # 2. Tentar Gemini
        if settings.GEMINI_API_KEY:
            gemini = GeminiProvider(settings.GEMINI_API_KEY)
            if await gemini.is_available():
                logging.info("Utilizando Provedor: Google Gemini")
                return gemini

        # 3. Tentar DeepSeek
        if settings.DEEPSEEK_API_KEY:
            deepseek = OpenAICompatibleProvider(
                api_key=settings.DEEPSEEK_API_KEY, 
                base_url="https://api.deepseek.com", 
                name="DeepSeek"
            )
            if await deepseek.is_available():
                logging.info("Utilizando Provedor: DeepSeek")
                return deepseek

        # 4. Tentar OpenAI (Fallback final)
        if settings.OPENAI_API_KEY:
            openai = OpenAICompatibleProvider(api_key=settings.OPENAI_API_KEY)
            if await openai.is_available():
                logging.info("Utilizando Provedor: OpenAI")
                return openai

        raise Exception("Nenhum provedor de IA disponível ou configurado corretamente.")
