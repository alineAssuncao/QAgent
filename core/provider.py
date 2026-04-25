import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import httpx

from core.config import settings
from core.middleware import provider_health

try:
    from google import genai
    from google.api_core import exceptions as google_exceptions
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
import openai
from openai import AsyncOpenAI


# ══════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS
# ══════════════════════════════════════════════════════════════
class RateLimitError(Exception):
    """Exceção levantada quando um Provedor atinge o limite de cota (429)."""

    def __init__(self, message: str, provider_name: str):
        super().__init__(message)
        self.provider_name = provider_name


# TIMEOUTS (em segundos)
# ══════════════════════════════════════════════════════════════
LLM_REQUEST_TIMEOUT = (
    180  # Timeout por chamada ao LLM (3 minutos para projetos maiores)
)
LLM_CONNECT_TIMEOUT = 10  # Timeout de conexão
LM_STUDIO_TIMEOUT = 60  # Reduzido de 1200 para 60 para fallback rápido


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


class OllamaProvider(BaseProvider):
    def __init__(self, base_url: str, model_name: str):
        super().__init__("Ollama", model_name)
        self.client = AsyncOpenAI(
            base_url=f"{base_url}/v1",
            api_key="ollama",
            timeout=LLM_REQUEST_TIMEOUT,
        )
        self.base_url = base_url

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                if response.status_code != 200:
                    return False
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return self.model_name in models
        except Exception:
            return False

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
            raise TimeoutError(f"Ollama não respondeu em {LLM_REQUEST_TIMEOUT}s")


class LMStudioProvider(BaseProvider):
    def __init__(self, base_url: str, model_name: str):
        super().__init__("LM Studio (Local)", model_name)
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key="lm-studio",
            timeout=LM_STUDIO_TIMEOUT,
        )
        self.base_url = base_url

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/models", timeout=5.0)
                return response.status_code == 200
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
        super().__init__("Google Gemini", "models/gemini-2.5-flash")
        if not HAS_GEMINI:
            raise ImportError("A biblioteca 'google-genai' não está instalada. Execute 'pip install google-genai' para usar este provedor.")
        self.client = genai.Client(api_key=api_key)
        self.api_key = api_key

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # Separar instrução de sistema e formatar mensagens
        system_instruction = None
        genai_contents = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                # O novo SDK prefere system_instruction separado
                system_instruction = content
            else:
                role = "model" if role == "assistant" else "user"
                # Evitar mensagens consecutivas com o mesmo papel (Gemini não permite)
                if genai_contents and genai_contents[-1]["role"] == role:
                    genai_contents[-1]["parts"][0]["text"] += f"\n\n{content}"
                else:
                    genai_contents.append({"role": role, "parts": [{"text": content}]})

        try:
            # Configuração da chamada
            kwargs = {
                "model": self.model_name,
                "config": {"temperature": 0.7}
            }
            if system_instruction:
                kwargs["config"]["system_instruction"] = system_instruction

            # Se houver apenas uma mensagem de conteúdo, simplificar
            if len(genai_contents) == 1 and genai_contents[0]["role"] == "user":
                kwargs["contents"] = genai_contents[0]["parts"][0]["text"]
            else:
                kwargs["contents"] = genai_contents

            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.models.generate_content,
                    **kwargs
                ),
                timeout=LLM_REQUEST_TIMEOUT,
            )
            return response.text

        except google_exceptions.ResourceExhausted:
            raise RateLimitError(f"Limite de cota atingido no {self.name}", self.name)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Gemini não respondeu em {LLM_REQUEST_TIMEOUT}s")
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                raise RateLimitError(
                    f"Limite de cota atingido no {self.name}", self.name
                )
            raise e


class OpenAICompatibleProvider(BaseProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        name: str = "OpenAI",
        model_name: str = None,
    ):
        if not model_name:
            model_name = (
                "gpt-4o-mini" if "openai" in name.lower() else "deepseek-chat"
            )
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
        except openai.RateLimitError:
            raise RateLimitError(f"Limite de cota atingido no {self.name}", self.name)
        except asyncio.TimeoutError:
            raise TimeoutError(f"{self.name} não respondeu em {LLM_REQUEST_TIMEOUT}s")
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                raise RateLimitError(
                    f"Limite de cota atingido no {self.name}", self.name
                )
            if "timeout" in str(e).lower():
                raise TimeoutError(f"{self.name} timeout após {LLM_REQUEST_TIMEOUT}s")
            raise e


class ProviderFactory:
    @staticmethod
    async def get_all_available_providers(
        preferred_name: Optional[str] = None,
    ) -> List[BaseProvider]:
        providers = []

        # 1. OpenAI (Prioridade — tem créditos)
        if settings.OPENAI_API_KEY:
            openai_prov = OpenAICompatibleProvider(api_key=settings.OPENAI_API_KEY)
            if await openai_prov.is_available() and provider_health.is_healthy("OpenAI"):
                providers.append(openai_prov)

        # 2. Gemini
        if settings.GEMINI_API_KEY:
            gemini = GeminiProvider(settings.GEMINI_API_KEY)
            if await gemini.is_available() and provider_health.is_healthy(
                "Google Gemini"
            ):
                providers.append(gemini)

        # 3. LM Studio (Local)
        if settings.LM_STUDIO_MODELS:
            models = [
                m.strip() for m in settings.LM_STUDIO_MODELS.split(",") if m.strip()
            ]
            for model_name in models:
                lm_studio = LMStudioProvider(
                    settings.LM_STUDIO_BASE_URL, model_name or ""
                )
                if await lm_studio.is_available() and provider_health.is_healthy(
                    "LM Studio"
                ):
                    providers.append(lm_studio)

        # 4. Ollama
        if settings.OLLAMA_MODELS:
            ollama_model = settings.OLLAMA_MODELS.split(",")[0].strip()
            ollama = OllamaProvider(settings.OLLAMA_BASE_URL, ollama_model)
            if await ollama.is_available() and provider_health.is_healthy("Ollama"):
                providers.append(ollama)

        # 5. OpenRouter
        if settings.OPENROUTER_API_KEY and settings.OPENROUTER_MODEL:
            openrouter = OpenAICompatibleProvider(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                name="OpenRouter",
                model_name=settings.OPENROUTER_MODEL,
            )
            if await openrouter.is_available() and provider_health.is_healthy(
                "OpenRouter"
            ):
                providers.append(openrouter)

        # 6. DeepSeek
        if settings.DEEPSEEK_API_KEY:
            deepseek = OpenAICompatibleProvider(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                name="DeepSeek",
            )
            if await deepseek.is_available() and provider_health.is_healthy("DeepSeek"):
                providers.append(deepseek)

        # Priorização
        if preferred_name:
            matching = [
                p for p in providers if preferred_name.lower() in p.name.lower()
            ]
            non_matching = [
                p for p in providers if preferred_name.lower() not in p.name.lower()
            ]
            providers = matching + non_matching

        return providers

    @staticmethod
    async def get_best_provider_for_task(
        task_type: str, preferred_name: Optional[str] = None
    ) -> List[BaseProvider]:
        """Retorna provedores otimizados para o tipo de tarefa."""
        all_providers = await ProviderFactory.get_all_available_providers(preferred_name)
        if not all_providers:
            return []

        if task_type in ["analise", "codificacao"]:
            # Prioriza o Provedor Padrão (OpenAI se configurado) ou Gemini
            pref = preferred_name or settings.DEFAULT_PROVIDER
            primary = [p for p in all_providers if pref.lower() in p.name.lower()]

            # Se não encontrou o primário, tenta Gemini como segunda opção de inteligência
            if not primary and "gemini" not in pref.lower():
                primary = [p for p in all_providers if "gemini" in p.name.lower()]

            others = [p for p in all_providers if p not in primary]
            return primary + others
        elif task_type in ["teste", "verificacao"]:
            # Prioriza Econômicos
            econ = [
                p
                for p in all_providers
                if any(
                    x in p.name.lower()
                    for x in ["studio", "ollama", "deepseek", "openrouter"]
                )
            ]
            others = [
                p
                for p in all_providers
                if not any(
                    x in p.name.lower()
                    for x in ["studio", "ollama", "deepseek", "openrouter"]
                )
            ]
            return econ + others

        return all_providers

    @staticmethod
    async def get_active_provider() -> BaseProvider:
        available = await ProviderFactory.get_all_available_providers()
        if available:
            return available[0]
        raise Exception("Nenhum provedor de IA disponível.")
