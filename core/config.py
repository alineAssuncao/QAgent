from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Bot Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ALLOWED_USER_IDS: str  # Carrega como string e depois faz parse para lista

    # IA Providers (Ordem de Fallback: LM Studio -> Ollama -> Gemini -> DeepSeek/OpenAI)
    LM_STUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LM_STUDIO_MODELS: str = ""  # Lista de modelos locais disponíveis
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODELS: str = ""  # Lista de modelos locais servidos pelo Ollama
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = ""
    OPENAI_API_KEY: str = ""
    DEFAULT_PROVIDER: str = "Google Gemini"  # Provedor preferencial padrão

    # Agent Core Settings
    MAX_ITERATIONS: int = 30
    MEMORY_WINDOW_SIZE: int = 10
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATABASE_PATH: str = str(BASE_DIR / "data" / "qagent.db")
    SKILLS_DIR: str = str(BASE_DIR / "agents" / "skills")
    PROJECTS_DIR: str = str(BASE_DIR / "projects")
    TMP_DIR: str = str(BASE_DIR / "tmp")
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_user_ids(self) -> List[int]:
        """Converte a string de IDs permitidos em uma lista de inteiros."""
        return [int(uid.strip()) for uid in self.TELEGRAM_ALLOWED_USER_IDS.split(",")]


# Instância única global das configurações
settings = Settings()
