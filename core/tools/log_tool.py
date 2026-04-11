import os
import logging
from datetime import datetime
from typing import Dict, Any
from core.tools.base import BaseTool

class UpdateLogTool(BaseTool):
    """Ferramenta para atualizar o log de execução (log.md) na raiz do projeto."""
    
    @property
    def name(self) -> str:
        return "update_log"

    @property
    def description(self) -> str:
        return (
            "Registra um evento detalhado no arquivo log.md do projeto. "
            "Use esta ferramenta para manter a auditoria do seu raciocínio (Thought) e ações."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Caminho raiz do projeto (ex: projects/flask)."
                },
                "phase": {
                    "type": "string",
                    "description": "Fase atual (ex: 'Analysis', 'Iteration 1', 'Refining')."
                },
                "content": {
                    "type": "string",
                    "description": "Conteúdo detalhado do log (seu Thought ou observação)."
                },
                "llm_info": {
                    "type": "string",
                    "description": "Opcional: Nome do provedor/modelo atual."
                }
            },
            "required": ["project_path", "phase", "content"]
        }

    async def execute(self, project_path: str, phase: str, content: str, llm_info: str = "") -> str:
        try:
            # Garante que o caminho aponte para dentro de 'projects/' se for apenas o nome do repo
            if not project_path.startswith("projects/") and not os.path.isabs(project_path):
                project_path = os.path.join("projects", project_path)

            if not os.path.exists(project_path):
                return f"Erro: O caminho do projeto '{project_path}' não existe. Certifique-se de usar o caminho relativo correto (ex: projects/flask)."

            log_path = os.path.join(project_path, "log.md")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Cabeçalho se o arquivo for novo
            header = ""
            if not os.path.exists(log_path):
                header = (
                    f"# QAgent Execution Log - {os.path.basename(project_path)}\n"
                    f"**Início do Log:** {timestamp}\n"
                    f"**LLM:** {llm_info}\n\n"
                    "---"
                )
            
            entry = (
                f"\n\n## [{phase}] - {timestamp}\n"
                f"{content}\n"
                "\n---"
            )
            
            mode = "a" if os.path.exists(log_path) else "w"
            with open(log_path, mode, encoding="utf-8") as f:
                if header:
                    f.write(header)
                f.write(entry)
                
            return f"Sucesso: Evento registrado em {log_path}"
        except Exception as e:
            logging.error(f"Erro ao atualizar log: {e}")
            return f"Erro: {str(e)}"
