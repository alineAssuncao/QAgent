import logging
import asyncio
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.config import settings
from core.middleware import provider_health
from google import genai
from openai import AsyncOpenAI


# ══════════════════════════════════════════════════════════════
# TIMEOUTS (em segundos)
# ══════════════════════════════════════════════════════════════
LLM_REQUEST_TIMEOUT = 90  # Timeout por chamada ao LLM
LLM_CONNECT_TIMEOUT = 10  # Timeout de conexão
LM_STUDIO_TIMEOUT = 300  # Local é mais lento, timeout maior


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
    def __init__(self, base_url: str, model_name: str):
        super().__init__("LM Studio (Local)", model_name)
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lm-studio",
            timeout=LM_STUDIO_TIMEOUT,
        )
        self.base_url = base_url
        self._cached_models = None

    async def _get_loaded_models(self) -> List[str]:
        if self._cached_models is not None:
            return self._cached_models
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models", timeout=2.0)
                if response.status_code != 200:
                    self._cached_models = []
                    return []
                data = response.json()
                self._cached_models = [m.get("id", "") for m in data.get("data", [])]
                return self._cached_models
        except Exception:
            self._cached_models = []
            return []

    async def is_available(self) -> bool:
        try:
            loaded_models = await self._get_loaded_models()
            if not loaded_models:
                return False
            return self.model_name in loaded_models
        except Exception:
            return False

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model_name, messages=messages
                ),
                timeout=LM_STUDIO_TIMEOUT,
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            raise TimeoutError(f"LM Studio não respondeu em {LM_STUDIO_TIMEOUT}s")


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__("Google Gemini", "models/gemini-2.0-flash")
        self.client = genai.Client(api_key=api_key)
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            # ── Converter formato OpenAI → Gemini com contexto completo ──
            # O SDK genai aceita uma lista de Content objects ou strings.
            # Montamos o prompt com TODO o histórico, não apenas a última msg.
            contents = []

            # System prompt vai como instrução inicial
            system_parts = []
            for msg in messages:
                if msg["role"] == "system":
                    system_parts.append(msg["content"])

            # Mensagens de conversa (user + assistant + observations)
            for msg in messages:
                if msg["role"] == "system":
                    continue
                role = "user" if msg["role"] in ("user",) else "model"
                contents.append(
                    genai.types.Content(
                        role=role,
                        parts=[genai.types.Part(text=msg["content"])],
                    )
                )

            # Se não há contents de conversa, usar apenas o prompt direto
            if not contents:
                contents = messages[-1]["content"]

            # Config com system instruction
            config = None
            if system_parts:
                config = genai.types.GenerateContentConfig(
                    system_instruction="\n".join(system_parts),
                )

            response = await asyncio.wait_for(
                self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config,
                ),
                timeout=LLM_REQUEST_TIMEOUT,
            )
            return response.text

        except asyncio.TimeoutError:
            raise TimeoutError(f"Gemini não respondeu em {LLM_REQUEST_TIMEOUT}s")


class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, api_key: str, base_url: str = None, name: str = "OpenAI"):
        model_name = "gpt-3.5-turbo" if "openai" in name.lower() else "deepseek-chat"
        super().__init__(name, model_name)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=LLM_REQUEST_TIMEOUT,
        )
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model_name, messages=messages
                ),
                timeout=LLM_REQUEST_TIMEOUT,
            )
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            raise TimeoutError(f"{self.name} não respondeu em {LLM_REQUEST_TIMEOUT}s")


class ProviderFactory:
    @staticmethod
    async def get_all_available_providers() -> List[BaseProvider]:
        providers = []

        # 1. LM Studio (Prioridade Local) - adiciona todos os modelos disponíveis
        if settings.LM_STUDIO_MODELS:
            models = [
                m.strip() for m in settings.LM_STUDIO_MODELS.split(",") if m.strip()
            ]
            for model_name in models:
                lm_studio = LMStudioProvider(settings.LM_STUDIO_BASE_URL, model_name)
                if await lm_studio.is_available() and provider_health.is_healthy(
                    "LM Studio"
                ):
                    providers.append(lm_studio)

        # 2. Gemini
        if settings.GEMINI_API_KEY:
            gemini = GeminiProvider(settings.GEMINI_API_KEY)
            if await gemini.is_available() and provider_health.is_healthy(
                "Google Gemini"
            ):
                providers.append(gemini)
            else:
                provider_health.mark_unhealthy("Google Gemini")

        # 3. DeepSeek
        if settings.DEEPSEEK_API_KEY:
            deepseek = OpenAICompatibleProvider(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                name="DeepSeek",
            )
            if await deepseek.is_available() and provider_health.is_healthy("DeepSeek"):
                providers.append(deepseek)
            else:
                provider_health.mark_unhealthy("DeepSeek")

        # 4. OpenAI
        if settings.OPENAI_API_KEY:
            openai = OpenAICompatibleProvider(api_key=settings.OPENAI_API_KEY)
            if await openai.is_available() and provider_health.is_healthy("OpenAI"):
                providers.append(openai)
            else:
                provider_health.mark_unhealthy("OpenAI")

        return providers

    @staticmethod
    async def get_active_provider() -> BaseProvider:
        """Apenas para retrocompatibilidade, retorna o primeiro disponível."""
        available = await ProviderFactory.get_all_available_providers()
        if available:
            return available[0]
        raise Exception("Nenhum provedor de IA disponível ou configurado corretamente.")
