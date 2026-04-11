import asyncio
import subprocess
import os
import platform
import logging
from typing import Dict, Any
from core.tools.base import BaseTool

class RunShellTool(BaseTool):
    @property
    def name(self) -> str:
        return "run_shell_command"

    @property
    def description(self) -> str:
        return "Executa comandos no shell do sistema operacional de forma síncrona/assíncrona. Use para rodar testes, linting, instalar dependências ou verificar o ambiente."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "O comando completo para executar no shell."
                },
                "cwd": {
                    "type": "string",
                    "description": "O diretório de trabalho para execução do comando. Se não fornecido, usa o diretório base do projeto."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Tempo máximo de espera em segundos.",
                    "default": 60
                }
            },
            "required": ["command"]
        }

    async def execute(self, command: str, cwd: str = None, timeout: int = 60) -> str:
        """Executa o comando e captura stdout/stderr."""
        if not command:
            return "Erro: Comando não fornecido."

        # Higienização básica de segurança (opcional, dependendo do uso)
        # Como o bot é para uso privado em ambiente controlado, permitimos execução direta.
        
        try:
            # Se cwd não for absoluto, resolver a partir do diretório do projeto ou settings
            from core.config import settings
            base_dir = settings.BASE_DIR
            
            working_dir = cwd if cwd and os.path.isabs(cwd) else os.path.join(base_dir, cwd) if cwd else base_dir
            
            if not os.path.exists(working_dir):
                return f"Erro: Diretório de trabalho '{working_dir}' não existe."

            # Usar shell=True no Windows, mas tomar cuidado
            use_shell = platform.system() == "Windows"
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir
            )

            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                stdout_str = stdout.decode("utf-8", errors="replace").strip()
                stderr_str = stderr.decode("utf-8", errors="replace").strip()
                
                result = []
                if stdout_str:
                    result.append(f"STDOUT:\n{stdout_str}")
                if stderr_str:
                    result.append(f"STDERR:\n{stderr_str}")
                
                final_output = "\n".join(result) if result else "Comando executado com sucesso (sem saída)."
                return f"Exit Code: {process.returncode}\n{final_output}"
                
            except asyncio.TimeoutError:
                process.kill()
                return f"Erro: O comando excedeu o timeout de {timeout}s."
                
        except Exception as e:
            logging.error(f"Erro ao executar shell command: {e}")
            return f"Erro na execução: {str(e)}"
