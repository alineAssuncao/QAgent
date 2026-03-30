import os
import asyncio
import logging
import re
from typing import Dict, Any, List, Optional
from core.tools.base import BaseTool
from core.config import settings


class RunShellTool(BaseTool):
    """
    Ferramenta para execução de comandos shell controlados.
    Implementa whitelist estrita e sanitização de inputs para segurança.
    """

    # ══════════════════════════════════════════════════════════════
    # WHITELIST DE COMANDOS PERMITIDOS
    # Apenas comandos desta lista podem ser executados.
    # Para adicionar um novo comando, inclua-o aqui E na documentação.
    # ══════════════════════════════════════════════════════════════
    ALLOWED_COMMANDS = {
        # Linters e Formatadores
        "ruff": "Linter/formatter Python ultrarrápido",
        "pylint": "Análise estática Python",
        "flake8": "Linter Python (PEP8)",
        "mypy": "Verificação de tipos Python",
        "eslint": "Linter JavaScript/TypeScript",
        "prettier": "Formatador de código multi-linguagem",

        # Ferramentas de Teste
        "pytest": "Framework de testes Python",
        "python": "Interpretador Python (para -m pytest, etc.)",
        "npm": "Gerenciador de pacotes Node.js (test, run)",
        "npx": "Executor de pacotes Node.js",
        "yarn": "Gerenciador de pacotes alternativo Node.js",
        "cargo": "Build system e package manager Rust",
        "mvn": "Build tool Java (Maven)",
        "gradle": "Build tool Java/Kotlin",
        "go": "Toolchain Go",
        "dotnet": "CLI .NET (test, build)",

        # Análise de Código
        "radon": "Métricas de complexidade Python",
        "lizard": "Análise de complexidade multi-linguagem",
        "bandit": "Análise de segurança Python",
        "semgrep": "Análise estática multi-linguagem",

        # Cobertura
        "coverage": "Ferramenta de cobertura Python",
        "nyc": "Cobertura de código JavaScript",

        # Git (somente leitura)
        "git": "Controle de versão (operações permitidas limitadas)",

        # Utilitários seguros
        "cat": "Exibir conteúdo de arquivo",
        "find": "Buscar arquivos",
        "wc": "Contar linhas/palavras",
        "tree": "Exibir árvore de diretórios",
        "dir": "Listar diretório (Windows)",
    }

    # Subcomandos Git permitidos (bloqueia push, force, etc. destrutivos)
    GIT_ALLOWED_SUBCOMMANDS = {
        "status", "log", "diff", "show", "branch", "tag",
        "ls-files", "rev-parse", "describe", "shortlog",
        "add", "commit",  # permitidos para o workflow de testes
    }

    # Padrões proibidos em qualquer argumento (segurança contra injection)
    FORBIDDEN_PATTERNS = [
        r"[;&|`$]",          # Operadores de shell / command chaining
        r"\.\./\.\.",        # Path traversal profundo
        r"rm\s+-rf",         # Remoção recursiva forçada
        r">(>?)\s*/",        # Redirecionamento para raiz
        r"curl.*\|.*sh",     # Download + execução
        r"wget.*\|.*sh",     # Download + execução
        r"eval\s+",          # Eval dinâmico
        r"exec\s+",          # Exec dinâmico
        r"powershell",       # Invocar outro shell
        r"cmd\s+/c",         # Invocar cmd
        r"del\s+/[sfq]",     # Deleção forçada Windows
    ]

    # Timeout padrão para execução de comandos (segundos)
    DEFAULT_TIMEOUT = 120
    MAX_TIMEOUT = 600

    @property
    def name(self) -> str:
        return "run_shell"

    @property
    def description(self) -> str:
        allowed = ", ".join(sorted(self.ALLOWED_COMMANDS.keys()))
        return (
            f"Executa comandos de shell controlados para análise de código, "
            f"linting e execução de testes. Comandos permitidos: {allowed}. "
            f"Todos os comandos são executados com whitelist e sanitização."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": (
                        "Comando a executar (ex: 'pytest --cov=src tests/', "
                        "'ruff check src/', 'npm test'). "
                        "O comando base deve estar na whitelist."
                    ),
                },
                "working_dir": {
                    "type": "string",
                    "description": (
                        "Diretório de trabalho relativo ao BASE_DIR "
                        "(ex: 'projects/my-repo'). Padrão: '.'"
                    ),
                },
                "timeout": {
                    "type": "integer",
                    "description": (
                        f"Timeout em segundos (padrão: {DEFAULT_TIMEOUT}, "
                        f"máximo: {MAX_TIMEOUT})."
                    ),
                },
            },
            "required": ["command"],
        }

    async def execute(
        self,
        command: str,
        working_dir: str = ".",
        timeout: int = None,
        **kwargs,
    ) -> str:
        # 1. Sanitizar e validar
        validation_error = self._validate_command(command)
        if validation_error:
            return f"❌ BLOQUEADO: {validation_error}"

        # 2. Resolver diretório de trabalho
        cwd = self._resolve_working_dir(working_dir)
        if not os.path.exists(cwd):
            return f"❌ Diretório não encontrado: {working_dir}"

        # 3. Resolver timeout
        effective_timeout = min(
            timeout or self.DEFAULT_TIMEOUT,
            self.MAX_TIMEOUT
        )

        # 4. Executar comando
        logging.info(f"[SHELL] Executando: {command} (cwd={cwd}, timeout={effective_timeout}s)")

        try:
            # No Windows, usamos shell=True para compatibilidade com npm, npx etc.
            is_windows = os.name == "nt"

            if is_windows:
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=self._get_safe_env(),
                )
            else:
                parts = command.split()
                process = await asyncio.create_subprocess_exec(
                    *parts,
                    cwd=cwd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=self._get_safe_env(),
                )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=effective_timeout,
            )

            stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""

            # 5. Limitar tamanho do output para não estourar contexto
            max_output = 8000
            if len(stdout_str) > max_output:
                stdout_str = stdout_str[:max_output] + "\n\n...[Output truncado]..."
            if len(stderr_str) > max_output:
                stderr_str = stderr_str[:max_output] + "\n\n...[Stderr truncado]..."

            status = "✅ Sucesso" if process.returncode == 0 else f"⚠️ Exit code: {process.returncode}"

            result = f"{status}\n\n"
            if stdout_str.strip():
                result += f"📤 STDOUT:\n{stdout_str}\n"
            if stderr_str.strip():
                result += f"📤 STDERR:\n{stderr_str}\n"

            if not stdout_str.strip() and not stderr_str.strip():
                result += "(Sem output)"

            return result

        except asyncio.TimeoutError:
            process.kill()
            return f"⏱️ TIMEOUT: Comando excedeu {effective_timeout}s e foi interrompido."
        except FileNotFoundError:
            return f"❌ Comando não encontrado no sistema. Verifique se está instalado."
        except Exception as e:
            logging.error(f"[SHELL] Erro: {e}")
            return f"❌ Erro ao executar comando: {str(e)}"

    def _validate_command(self, command: str) -> Optional[str]:
        """
        Valida o comando contra a whitelist e padrões proibidos.
        Retorna None se válido, ou mensagem de erro se inválido.
        """
        if not command or not command.strip():
            return "Comando vazio."

        # Extrair o comando base (primeiro token)
        parts = command.strip().split()
        base_command = parts[0].lower()

        # Remover path se presente (ex: /usr/bin/pytest → pytest)
        base_command = os.path.basename(base_command)

        # Remover extensão .exe no Windows
        if base_command.endswith(".exe"):
            base_command = base_command[:-4]

        # Verificar whitelist
        if base_command not in self.ALLOWED_COMMANDS:
            allowed = ", ".join(sorted(self.ALLOWED_COMMANDS.keys()))
            return (
                f"Comando '{base_command}' não está na whitelist. "
                f"Comandos permitidos: {allowed}"
            )

        # Verificar subcomandos Git
        if base_command == "git" and len(parts) > 1:
            git_subcommand = parts[1].lower()
            if git_subcommand not in self.GIT_ALLOWED_SUBCOMMANDS:
                allowed_git = ", ".join(sorted(self.GIT_ALLOWED_SUBCOMMANDS))
                return (
                    f"Subcomando git '{git_subcommand}' não permitido. "
                    f"Subcomandos Git permitidos: {allowed_git}"
                )

        # Verificar padrões proibidos
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    f"Comando contém padrão proibido (possível injeção). "
                    f"Padrão detectado: {pattern}"
                )

        return None

    def _resolve_working_dir(self, working_dir: str) -> str:
        """Resolve o diretório de trabalho de forma segura."""
        if os.path.isabs(working_dir):
            # Se for absoluto, verificar se está dentro do BASE_DIR
            abs_path = os.path.normpath(working_dir)
            base = os.path.normpath(settings.BASE_DIR)
            if not abs_path.startswith(base):
                return os.path.join(settings.BASE_DIR, "projects")
            return abs_path

        full_path = os.path.normpath(os.path.join(settings.BASE_DIR, working_dir))

        # Verificar path traversal
        base = os.path.normpath(settings.BASE_DIR)
        if not full_path.startswith(base):
            return settings.BASE_DIR

        return full_path

    def _get_safe_env(self) -> Dict[str, str]:
        """Retorna variáveis de ambiente seguras para o subprocesso."""
        safe_env = os.environ.copy()
        # Remover variáveis sensíveis do ambiente do subprocesso
        sensitive_vars = [
            "TELEGRAM_BOT_TOKEN",
            "GEMINI_API_KEY",
            "DEEPSEEK_API_KEY",
            "OPENAI_API_KEY",
        ]
        for var in sensitive_vars:
            safe_env.pop(var, None)
        return safe_env
