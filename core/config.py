import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Bot Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ALLOWED_USER_IDS: str  # Carrega como string e depois faz parse para lista
    
    # IA Providers (Ordem de Fallback: LM Studio -> Gemini -> DeepSeek/OpenAI)
    LM_STUDIO_BASE_URL: str = "http://localhost:1234/v1"
    LM_STUDIO_MODELS: str = ""  # Lista de modelos locais disponíveis
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Agent Core Settings
    MAX_ITERATIONS: int = 5
    MEMORY_WINDOW_SIZE: int = 10
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATABASE_PATH: str = str(BASE_DIR / "data" / "qagent.db")
    SKILLS_DIR: str = str(BASE_DIR / "agents" / "skills")
    TMP_DIR: str = str(BASE_DIR / "tmp")
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_user_ids(self) -> List[int]:
        """Converte a string de IDs permitidos em uma lista de inteiros."""
        return [int(uid.strip()) for uid in self.TELEGRAM_ALLOWED_USER_IDS.split(",")]

# Instância única global das configurações
settings = Settings()
