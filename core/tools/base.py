from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    def parameters(self) -> Dict[str, Any]:
        """OpenAI-style parameters schema."""
        return {}

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Executa a ferramenta e retorna o resultado como string."""
        pass
