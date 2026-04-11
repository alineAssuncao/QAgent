import os
import asyncio
import logging
from typing import Dict, Any, Optional
from core.tools.base import BaseTool
from core.config import settings


class CloneRepositoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "clone_repository"

    @property
    def description(self) -> str:
        return "Clona um repositório Git público para a pasta 'projects/' local. Retorna o CAMINHO RELATIVO (ex: 'projects/repo') que deve ser usado obrigatoriamente em outras ferramentas."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "A URL do repositório Git (ex: https://github.com/user/repo.git).",
                },
                "folder_name": {
                    "type": "string",
                    "description": "Opcional: Nome da pasta de destino dentro de 'projects/'. Se omitido, usa o nome do repo.",
                },
            },
            "required": ["url"],
        }

    async def execute(
        self, url: str, folder_name: Optional[str] = None, **kwargs
    ) -> str:
        if not folder_name:
            folder_name = url.split("/")[-1].replace(".git", "")

        target_dir = os.path.join(settings.PROJECTS_DIR, folder_name)

        if os.path.exists(target_dir):
            logging.info(
                f"Repositório {folder_name} já existe. Atualizando com pull..."
            )
            try:
                await self._run_git_command(["git", "-C", target_dir, "fetch"])
                await self._run_git_command(
                    ["git", "-C", target_dir, "reset", "--hard", "HEAD"]
                )
                return f"Sucesso: O repositório já existia em '{os.path.relpath(target_dir, settings.BASE_DIR)}', foi atualizado com git fetch + reset --hard HEAD."
            except Exception as e:
                return f"Erro ao atualizar repositório existente: {str(e)}"

        os.makedirs(settings.PROJECTS_DIR, exist_ok=True)

        try:
            logging.info(f"Clonando {url} para {target_dir}...")
            await self._run_git_command(
                ["git", "clone", "--depth", "1", url, target_dir]
            )
            relative_path = os.path.relpath(target_dir, settings.BASE_DIR)
            return f"Sucesso: Repositório clonado em '{relative_path}'. Você agora pode explorar este diretório usando 'list_directory' ou 'read_file'."
        except Exception as e:
            error_msg = str(e)
            return f"Erro ao clonar repositório: {error_msg}"

    async def _run_git_command(self, args: list[str]) -> str:
        """Executa um comando git de forma assíncrona."""
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(stderr.decode("utf-8", errors="replace") if stderr else "Comando git falhou")

        return stdout.decode("utf-8", errors="replace") if stdout else ""
