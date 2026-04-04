import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from core.tools.base import BaseTool
from core.config import settings


class GitManagementTool(BaseTool):
    @property
    def name(self) -> str:
        return "git_manage"

    @property
    def description(self) -> str:
        return "Executa operações avançadas de Git (add, commit, push) e roda testes em repositório clonado."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["commit", "push", "run_tests", "detect_tests"],
                    "description": "Ação: commit, push, run_tests (roda testes), detect_tests (detecta framework).",
                },
                "repo_path": {
                    "type": "string",
                    "description": "Caminho relativo do repositório (ex: 'projects/my-repo').",
                },
                "commit_message": {
                    "type": "string",
                    "description": "Mensagem para o commit (obrigatório para action='commit').",
                },
            },
            "required": ["action", "repo_path"],
        }

    async def execute(
        self,
        action: str,
        repo_path: str,
        commit_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        if not repo_path.startswith("projects/") and not repo_path.startswith(
            "projects\\"
        ):
            repo_path = os.path.join("projects", repo_path)

        full_repo_path = os.path.join(settings.BASE_DIR, repo_path)

        if not os.path.exists(full_repo_path):
            return f"Erro: O caminho '{repo_path}' não existe."

        if action == "detect_tests":
            return await self._detect_test_framework(full_repo_path)
        elif action == "run_tests":
            return await self._run_tests(full_repo_path)
        elif action == "commit":
            if not commit_message:
                return "Erro: Mensagem de commit é obrigatória."
            return await self._git_commit(full_repo_path, commit_message)
        elif action == "push":
            return await self._git_push(full_repo_path)

        return "Ação desconhecida."

    async def _detect_test_framework(self, repo_path: str) -> str:
        """Detecta qual framework de teste o projeto usa."""
        language_files = {
            "Python": [
                "requirements.txt",
                "pyproject.toml",
                "setup.py",
                "setup.cfg",
                "Pipfile",
            ],
            "JavaScript/TypeScript": ["package.json", "package-lock.json", "yarn.lock"],
            "Java": ["pom.xml", "build.gradle", "build.gradle.kts"],
            "C#": [".csproj", ".sln"],
            "Go": ["go.mod"],
            "Rust": ["Cargo.toml"],
        }

        test_files = [
            ("package.json", "npm test / yarn test", "Node.js"),
            ("pytest.ini", "pytest", "Python"),
            ("setup.py", "pytest", "Python"),
            ("pyproject.toml", "pytest", "Python"),
            ("Cargo.toml", "cargo test", "Rust"),
            ("pom.xml", "mvn test", "JDK"),
            ("build.gradle", "gradle test", "JDK"),
            ("go.mod", "go test", "Go"),
        ]

        languages_detected = []
        for lang, files in language_files.items():
            for filename in files:
                if os.path.exists(os.path.join(repo_path, filename)):
                    languages_detected.append(lang)
                    break

        if not languages_detected:
            for root, dirs, files in os.walk(repo_path):
                if any(f.endswith(".py") for f in files):
                    languages_detected.append("Python")
                    break

        test_files_in_dir = []
        for root, dirs, files in os.walk(repo_path):
            for f in files:
                if f.startswith("test_") and f.endswith(".py"):
                    test_files_in_dir.append(f)
                elif f.endswith("_test.py"):
                    test_files_in_dir.append(f)

        frameworks_detected = []
        for filename, cmd, prereq in test_files:
            if os.path.exists(os.path.join(repo_path, filename)):
                frameworks_detected.append(f"- {filename}: usar `{cmd}`")

        if (
            "Python" in languages_detected
            and test_files_in_dir
            and not frameworks_detected
        ):
            frameworks_detected.append("- arquivos de teste detectados: usar `pytest`")

        if "Python" in languages_detected and not frameworks_detected:
            frameworks_detected.append("- script avulso: usar `pytest`")

        result = "Linguagem detectada: " + ", ".join(set(languages_detected)) + "\n\n"
        result += "Frameworks de teste:\n" + "\n".join(frameworks_detected) + "\n\n"
        result += "Pré-requisitos necessários:\n"

        prereqs_needed = set()
        for _, _, prereq in test_files:
            if os.path.exists(
                os.path.join(repo_path, [f for f, _, p in test_files if p == prereq][0])
            ):
                prereqs_needed.add(prereq)

        if "Python" in languages_detected and not prereqs_needed:
            prereqs_needed.add("Python")

        for prereq in prereqs_needed:
            installed = self._check_prerequisite(prereq)
            status = "✅" if installed else "❌"
            result += f"- {prereq}: {status}\n"

        return result

    def _check_prerequisite(self, prereq: str) -> bool:
        """Verifica se um pré-requisito está instalado."""
        import shutil

        prereq_commands = {
            "Python": ["python", "python3"],
            "Node.js": ["node", "npm"],
            "JDK": ["java", "javac"],
            "Go": ["go"],
            "Rust": ["cargo"],
        }

        commands = prereq_commands.get(prereq, [])
        return any(shutil.which(cmd) for cmd in commands)

    async def _run_tests(self, repo_path: str) -> str:
        """Executa testes detectando automaticamente o framework."""
        logging.info(f"Executando testes em {repo_path}")

        test_commands = [
            ("package.json", ["npm", "test"]),
            (
                "pytest.ini",
                [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=.",
                    "--cov-report=term",
                    "--maxfail=5",
                ],
            ),
            (
                "pyproject.toml",
                [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=.",
                    "--cov-report=term",
                    "--maxfail=5",
                ],
            ),
            ("setup.py", ["python", "-m", "pytest", "--cov=.", "--cov-report=term"]),
            ("Cargo.toml", ["cargo", "test"]),
            ("pom.xml", ["mvn", "clean", "test", "jacoco:report"]),
        ]

        for filename, cmd in test_commands:
            if os.path.exists(os.path.join(repo_path, filename)):
                try:
                    result = await self._run_command(cmd, cwd=repo_path)
                    status = "✅ Sucesso" if result.returncode == 0 else "❌ Falha"

                    if filename == "pom.xml":
                        jacoco_csv = os.path.join(
                            repo_path, "target", "site", "jacoco", "jacoco.csv"
                        )
                        if os.path.exists(jacoco_csv):
                            import csv

                            with open(jacoco_csv, mode="r", encoding="utf-8") as f:
                                reader = csv.DictReader(f)
                                missed = 0
                                covered = 0
                                for row in reader:
                                    missed += int(row["INSTRUCTION_MISSED"])
                                    covered += int(row["INSTRUCTION_COVERED"])
                                if (missed + covered) > 0:
                                    percent = int((covered / (covered + missed)) * 100)
                                    result.stdout += f"\nTotal coverage: {percent}%\n"

                    return f"{status} ({' '.join(cmd)}):\n\n{result.stdout}\n{result.stderr}"
                except FileNotFoundError:
                    return f"Comando {' '.join(cmd)} não encontrado. Instale o framework necessário."
                except Exception as e:
                    return f"Erro ao executar: {str(e)}"

        has_test_python_files = False
        logging.info(f"[GIT_MANAGE] Searching for test files in {repo_path}")
        for root, dirs, files in os.walk(repo_path):
            test_files_found = [
                f
                for f in files
                if f.endswith(".py")
                and (f.startswith("test_") or f.endswith("_test.py"))
            ]
            if test_files_found:
                logging.info(
                    f"[GIT_MANAGE] Found test files: {test_files_found} in {root}"
                )
                has_test_python_files = True
                break
            if "tests" in dirs:
                tests_dir = os.path.join(root, "tests")
                if os.path.isdir(tests_dir):
                    for f in os.listdir(tests_dir):
                        if f.endswith(".py"):
                            logging.info(f"[GIT_MANAGE] Found test file in tests/: {f}")
                            has_test_python_files = True
                            break
                    if has_test_python_files:
                        break
            if "tests" in dirs:
                tests_dir = os.path.join(root, "tests")
                if os.path.isdir(tests_dir):
                    for f in os.listdir(tests_dir):
                        if f.endswith(".py"):
                            has_test_python_files = True
                            break
                    if has_test_python_files:
                        break

        if has_test_python_files:
            try:
                cmd = [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=.",
                    "--cov-report=term",
                    "--maxfail=5",
                ]
                result = await self._run_command(cmd, cwd=repo_path)
                status = "✅ Sucesso" if result.returncode == 0 else "❌ Falha"
                return (
                    f"{status} ({' '.join(cmd)}):\n\n{result.stdout}\n{result.stderr}"
                )
            except FileNotFoundError:
                return "Comando pytest não encontrado. Instale o framework necessário."
            except Exception as e:
                return f"Erro ao executar: {str(e)}"

        return "❌ Nenhum framework de teste detectado no projeto."

    async def _git_commit(self, repo_path: str, message: str) -> str:
        result = await self._run_command(["git", "-C", repo_path, "add", "."])
        if result.returncode != 0:
            return f"Erro no git add: {result.stderr}"

        result = await self._run_command(
            ["git", "-C", repo_path, "commit", "-m", message]
        )
        if "nothing to commit" in result.stderr:
            return "Aviso: Nada para commitar."
        return f"✅ Commitado: '{message}'"

    async def _git_push(self, repo_path: str) -> str:
        result = await self._run_command(["git", "-C", repo_path, "push"])
        if result.returncode == 0:
            return "✅ Push realizado com sucesso."
        return f"Erro no push: {result.stderr}"

    async def _run_command(
        self, cmd: List[str], cwd: str
    ) -> asyncio.subprocess.Process:
        """Executa um comando de forma assíncrona."""
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        class Result:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout.decode() if stdout else ""
                self.stderr = stderr.decode() if stderr else ""

        return Result(process.returncode, stdout, stderr)
