import logging
import json
from typing import List, Dict, Any, Optional
from core.tools.base import BaseTool

class ToolManager:
    def __init__(self, tools: List[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}

    def get_tool_definitions(self) -> str:
        """Retorna uma string formatada com os nomes e descrições das ferramentas para o prompt."""
        if not self.tools:
            return "Nenhuma ferramenta disponível."
            
        definitions = []
        for tool in self.tools.values():
            params = json.dumps(tool.parameters, indent=2, ensure_ascii=False)
            definitions.append(f"- {tool.name}: {tool.description}\n  Parâmetros: {params}")
        
        return "\n".join(definitions)

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Executa a ferramenta pelo nome com os argumentos fornecidos."""
        tool = self.tools.get(name)
        if not tool:
            return f"Erro: Ferramenta '{name}' não encontrada."
        
        try:
            logging.info(f"Executando ferramenta: {name} com args: {arguments}")
            return await tool.execute(**arguments)
        except Exception as e:
            return f"Erro ao executar '{name}': {str(e)}"
