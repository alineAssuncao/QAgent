import logging
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.config import settings
from google import genai
from openai import AsyncOpenAI

class BaseProvider(ABC):
    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name

    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

class LMStudioProvider(BaseProvider):
    def __init__(self, base_url: str):
        super().__init__("LM Studio (Local)", "local-model")
        self.client = AsyncOpenAI(base_url=base_url, api_key="lm-studio")
        self.base_url = base_url

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models", timeout=2.0)
                if response.status_code != 200:
                    return False
                data = response.json()
                # LM Studio retorna uma lista de modelos no campo 'data'. 
                # Se estiver vazio, não há modelo carregado apesar do servidor estar ON.
                return len(data.get("data", [])) > 0
        except Exception:
            return False

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__("Google Gemini", "models/gemini-1.5-pro")
        self.client = genai.Client(api_key=api_key)
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # Convertendo mensagens para o formato do novo SDK (google-genai)
        # O Prompt final é a última mensagem do role 'user'
        prompt = messages[-1]['content']
        # O SDK v1+ gerencia o chat ou chamadas de modelo únicas
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text

class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str = None, name: str = "OpenAI"):
        model_name = "gpt-3.5-turbo" if "openai" in name.lower() else "deepseek-chat"
        super().__init__(name, model_name)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

class ProviderFactory:
    @staticmethod
    async def get_all_available_providers() -> List[BaseProvider]:
        providers = []

        # 1. LM Studio (Prioridade Local)
        lm_studio = LMStudioProvider(settings.LM_STUDIO_BASE_URL)
        if await lm_studio.is_available():
            providers.append(lm_studio)

        # 2. Gemini
        if settings.GEMINI_API_KEY:
            gemini = GeminiProvider(settings.GEMINI_API_KEY)
            if await gemini.is_available():
                providers.append(gemini)

        # 3. DeepSeek
        if settings.DEEPSEEK_API_KEY:
            deepseek = OpenAICompatibleProvider(
                api_key=settings.DEEPSEEK_API_KEY, 
                base_url="https://api.deepseek.com", 
                name="DeepSeek"
            )
            if await deepseek.is_available():
                providers.append(deepseek)

        # 4. OpenAI
        if settings.OPENAI_API_KEY:
            openai = OpenAICompatibleProvider(api_key=settings.OPENAI_API_KEY)
            if await openai.is_available():
                providers.append(openai)

        return providers

    @staticmethod
    async def get_active_provider() -> BaseProvider:
        """Apenas para retrocompatibilidade, retorna o primeiro disponível."""
        available = await ProviderFactory.get_all_available_providers()
        if available:
            return available[0]
        raise Exception("Nenhum provedor de IA disponível ou configurado corretamente.")
