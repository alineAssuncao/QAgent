from typing import Dict, Any
from core.tools.base import BaseTool
from skills.loader import SkillLoader

class SkillActivationTool(BaseTool):
    def __init__(self, skill_loader: SkillLoader):
        self._loader = skill_loader

    @property
    def name(self) -> str:
        return "activate_skill"

    @property
    def description(self) -> str:
        return "Ativa e lê as instruções completas de uma habilidade (skill) específica. Use quando decidir delegar uma tarefa para uma sub-skill especialista."

    @property
    def parameters(self) -> Dict[str, Any]:
        available = [s['name'] for s in self._loader.skills]
        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "enum": available,
                    "description": "O nome da skill para carregar as instruções completas."
                }
            },
            "required": ["skill_name"]
        }

    async def execute(self, skill_name: str) -> str:
        skill = self._loader.get_skill_by_name(skill_name)
        if not skill:
            return f"Erro: Skill '{skill_name}' não encontrada ou não carregada."
        
        full_instruction = skill.get('full_instruction', 'Instruções não disponíveis.')
        return f"Instruções Ativadas para '{skill_name}':\n\n{full_instruction}"
