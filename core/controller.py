import logging
import os
import asyncio
import shutil
import re
from enum import Enum
from datetime import datetime
from core.config import settings
from typing import Optional, Dict, Any
from core.provider import ProviderFactory, BaseProvider
from core.loop import AgentLoop
from core.middleware import rate_limiter
from skills.loader import SkillLoader
from memory.repository import MessageRepository
from memory.database import Database
from handlers.input import TelegramInputHandler
from handlers.output import TelegramOutputHandler
from aiogram import types


class TesteEstado(Enum):
    ANALISE = "analise"
    AGUARDANDO_CONFIRMACAO = "aguardando_confirmacao"
    EXECUTANDO = "executando"
    FINALIZADO = "finalizado"


# Mapeamento de palavras-chave para tipo de teste
TEST_TYPE_KEYWORDS = {
    "unitario": ["unit[aáàã]rio", "unitário", "unit test"],
    "integracao": ["integra[cç][aã]o", "integration test", "testar m[oó]dulos"],
    "api": ["testar api", "endpoint", "rest", "graphql", "contract"],
    "frontend": ["frontend", "componente", "react test", "vue test", "playwright", "cypress", "testar ui"],
    "analise": ["analisar c[oó]digo", "code review", "qualidade", "code smell", "complexidade"],
    "relatorio": ["relat[oó]rio", "dashboard", "m[eé]tricas", "cobertura"],
    "refatorar": ["refatorar", "testabilidade", "refactoring", "desacoplar"],
    "cicd": ["pipeline", "ci/cd", "github actions", "gitlab ci"],
    "documentar": ["documentar teste", "plano de teste", "test plan", "bdd", "gherkin", "rastreabilidade"],
}

# Keywords genéricos que ativam o QA Maestro (qualquer tipo de teste)
QA_KEYWORDS = [
    r"teste", r"test", r"testar", r"cobertura", r"coverage",
    r"qualidade", r"quality", r"automa[cç][aã]o",
    r"analisar", r"relat[oó]rio", r"refatorar", r"pipeline",
    r"documentar", r"plano de teste",
]

class QATestContext:
    def __init__(self):
        self.estado: TesteEstado = TesteEstado.ANALISE
        self.user_id: int = 0
        self.chat_id: int = 0
        self.repo_name: str = ""
        self.repo_path: str = ""
        self.git_url: Optional[str] = None
        self.test_type: str = "unitario"  # tipo de teste detectado
        self.cobertura_inicial: str = "0%"
        self.cobertura_final: str = "0%"
        self.frameworks: str = ""
        self.estrutura: str = ""
        self.recomendacoes: str = ""
        self.progresso_task: Optional[asyncio.Task] = None
        self.start_time: Optional[datetime] = None
        self.erro_encontrado: bool = False


class AgentController:
    def __init__(self):
        self.skill_loader = SkillLoader(skills_dir=settings.SKILLS_DIR)
        self.active_provider: Optional[BaseProvider] = None
        self.running_tasks: Dict[int, asyncio.Task] = {}
        self.contextos: Dict[int, QATestContext] = {}

    async def initialize(self):
        await Database.init_db()
        self.skill_loader.load_all_skills()
        logging.info("AgentController inicializado.")

    async def handle_message(self, message: types.Message):
        user_id = message.from_user.id
        user_input = ""
        requires_audio = False

        if message.text:
            user_input = message.text
        elif message.voice or message.audio:
            user_input = await TelegramInputHandler.process_voice(message)
            requires_audio = True
        elif message.document:
            if message.document.file_name.endswith(".pdf"):
                user_input = await TelegramInputHandler.process_pdf(message)
                if message.caption:
                    user_input = f"{user_input}\n{message.caption}"
            elif message.document.file_name.endswith(".py"):
                user_input = await TelegramInputHandler.process_python_file(message)
            else:
                await message.reply(
                    "⚠️ Atualmente só suporto PDFs, scripts Python (.py) e Áudio além de texto."
                )
                return

        if not user_input:
            return

        if not rate_limiter.is_allowed(user_id):
            remaining = rate_limiter.get_remaining_time(user_id)
            await message.reply(
                f"⏳ Aguarde {remaining}s antes de enviar outra mensagem."
            )
            return

        if user_id in self.contextos:
            contexto = self.contextos[user_id]
            if contexto.estado == TesteEstado.AGUARDANDO_CONFIRMACAO:
                if user_input.lower() in [
                    "sim",
                    "sim, pode",
                    "pode",
                    "pode prosseguir",
                    "ok",
                    "continuar",
                    "sim!",
                    "✅",
                    "sim ",
                ]:
                    await self._continuar_execucao(user_id)
                    return
                elif user_input.lower() in ["não", "nao", "cancelar", "cancela", "❌"]:
                    await self._cancelar_execucao(user_id, message)
                    return

        lower_input = user_input.lower()
        if any(w in lower_input for w in ["cancelar", "parar", "cancel"]):
            if user_id in self.running_tasks and not self.running_tasks[user_id].done():
                self.running_tasks[user_id].cancel()
                await message.reply("🛑 **Processamento Cancelado.**")
            if user_id in self.contextos:
                del self.contextos[user_id]
            return

        # Detectar tipo de teste solicitado
        test_type = self._detectar_tipo_teste(lower_input)
        
        # Verificar se há alguma keyword de QA na mensagem
        has_qa_keyword = any(
            re.search(kw, lower_input) for kw in QA_KEYWORDS
        )
        
        git_match = re.search(r"(https?://\S+\.git)", user_input)

        local_path_match = re.search(
            r"(?:projects[/\\])?([\w\-_]+)",
            user_input.split(":")[-1] if ":" in user_input else user_input,
        )
        local_path = local_path_match.group(1) if local_path_match else None
        has_local_path = local_path and os.path.exists(
            os.path.join(settings.PROJECTS_DIR, local_path)
        )

        if not has_qa_keyword and not git_match:
            await message.reply(
                "🤖 Sou o **QAgent** — especialista em automação de testes!\n\n"
                "Inclua na mensagem o **tipo de teste** + **link .git** ou **nome do projeto**.\n\n"
                "📋 **Tipos de teste suportados:**\n"
                "• Teste Unitário\n"
                "• Teste de Integração\n"
                "• Teste de API\n"
                "• Teste de Frontend\n"
                "• Análise de Código\n"
                "• Refatoração\n"
                "• Relatório de Cobertura\n"
                "• Pipeline CI/CD\n"
                "• Documentação de Testes"
            )
            return

        if git_match:
            git_url = git_match.group(1)
            await self._iniciar_fluxo_qa(
                message, git_url=git_url, local_path=None,
                requires_audio=requires_audio, test_type=test_type
            )
        elif has_local_path:
            await self._iniciar_fluxo_qa(
                message, git_url=None, local_path=local_path,
                requires_audio=requires_audio, test_type=test_type
            )
        else:
            await message.reply(
                "📁 Repositório não encontrado em `projects/`.\n"
                "Ou envie um **link .git** para clonar."
            )

    def _detectar_tipo_teste(self, lower_input: str) -> str:
        """Detecta o tipo de teste solicitado baseado em keywords."""
        for test_type, patterns in TEST_TYPE_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, lower_input):
                    return test_type
        return "unitario"  # padrão: teste unitário

    async def _iniciar_fluxo_qa(
        self,
        message: types.Message,
        git_url: str | None,
        local_path: str | None,
        requires_audio: bool,
        test_type: str = "unitario",
    ):
        user_id = message.from_user.id
        chat_id = message.chat.id

        contexto = QATestContext()
        contexto.user_id = user_id
        contexto.chat_id = chat_id
        contexto.git_url = git_url
        contexto.test_type = test_type
        contexto.start_time = datetime.now()
        self.contextos[user_id] = contexto

        try:
            msg = await message.reply("🔄 **Iniciando análise do repositório...**")

            if git_url:
                await msg.edit_text("📥 **Clonando repositório...**")
                from core.tools.git import CloneRepositoryTool

                clone_tool = CloneRepositoryTool()
                await clone_tool.execute(url=git_url)
                contexto.repo_name = git_url.split("/")[-1].replace(".git", "")
                contexto.repo_path = f"projects/{contexto.repo_name}"
                await msg.edit_text(f"✅ **Repositório clonado:** {contexto.repo_name}")
            else:
                contexto.repo_name = local_path or "unknown"
                contexto.repo_path = f"projects/{contexto.repo_name}"
                await msg.edit_text(
                    f"✅ **Usando repositório local:** {contexto.repo_name}"
                )

            await self._analisar_repositorio(msg, contexto, user_id)

        except Exception as e:
            logging.error(f"Erro no fluxo de teste unitário: {e}")
            await TelegramOutputHandler.send_response(chat_id, f"❌ **Erro:** {str(e)}")
            if user_id in self.contextos:
                del self.contextos[user_id]

    async def _analisar_repositorio(
        self, msg: types.Message, contexto: QATestContext, user_id: int
    ):
        from core.tools.repository import ListDirectoryTool
        from core.tools.git_management import GitManagementTool

        from core.tools.skills import SkillActivationTool

        await msg.edit_text("🔍 **Analisando estrutura do repositório...**")

        list_tool = ListDirectoryTool()
        estrutura = await list_tool.execute(path=contexto.repo_path)
        contexto.estrutura = estrutura

        await msg.edit_text("🛠️ **Detectando frameworks de teste...**")

        git_tool = GitManagementTool()
        frameworks = await git_tool.execute(
            action="detect_tests", repo_path=contexto.repo_path
        )
        contexto.frameworks = frameworks

        if not self._projeto_e_legivel_para_testes(frameworks):
            await msg.delete()
            await TelegramOutputHandler.send_response(
                contexto.chat_id,
                f"""❌ **Projeto não elegível para testes unitários**

━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ **Projeto:** {contexto.repo_name}

🗣️ **Linguagem detectada:** {self._extrair_linguagem(frameworks)}

⚠️ **Motivo:** O projeto não possui uma linguagem de programação detectada ou não possui arquivos fonte compatíveis com testes unitários automatizados.

📝 **O que isso significa:**
• O repositório pode não ter código fonte (apenas文档ação, configurações, etc.)
• A linguagem utilizada pode não ser suportada para automação de testes unitários
• Pode ser um projeto de infraestrutura, configuração ou sem código executável

💡 **Sugestão:**
• Verifique se o repositório contém código fonte
• Considere usar testes de integração para este projeto
• Este projeto pode precisar de abordagem manual de QA

━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
            )
            if user_id in self.contextos:
                del self.contextos[user_id]
            return

        await msg.edit_text("📊 **Executando testes atuais para medir cobertura...**")

        resultado_testes = await git_tool.execute(
            action="run_tests", repo_path=contexto.repo_path
        )

        cobertura = self._extrair_cobertura(resultado_testes)
        contexto.cobertura_inicial = cobertura

        contexto.recomendacoes = self._gerar_recomendacoes(estrutura, frameworks)

        await msg.delete()

        relatorio = f"""📊 **RELATÓRIO DE ANÁLISE**

 ━━━━━━━━━━━━━━━━━━━━━━━━━━

 🏷️ **Nome do Projeto:** {contexto.repo_name}

 📈 **Cobertura de Testes Atual:** {contexto.cobertura_inicial}

 🗣️ **Linguagem de Programação:**
 {self._extrair_linguagem(contexto.frameworks)}

 🔧 **Ferramentas para Testes Unitários:**
 {self._extrair_frameworks(contexto.frameworks)}

 ⚠️ **Pré-Requisitos Necessários:**
 {self._extrair_prerequisitos(contexto.frameworks)}

 💡 **O que pode ser melhorado para 100% de cobertura:**
 {contexto.recomendacoes}

 ━━━━━━━━━━━━━━━━━━━━━━━━━━

 ✅ **Posso prosseguir com a criação dos testes unitários?**

 (Responda **SIM** para continuar ou **NÃO** para cancelar)
 """

        await TelegramOutputHandler.send_response(contexto.chat_id, relatorio)

        contexto.estado = TesteEstado.AGUARDANDO_CONFIRMACAO

    def _extrair_cobertura(self, output_testes: str) -> str:
        padroes_cobertura = [
            r"(\d+)%\s*coverage",
            r"coverage.*?(\d+)%",
            r"(\d+)%\s*covered",
            r"COVERAGE.*?(\d+)%",
            r"Total.*?(\d+)%",
            r"Branch.*?(\d+)%",
        ]

        output_lower = output_testes.lower()
        for padrao in padroes_cobertura:
            match = re.search(padrao, output_lower)
            if match:
                return f"{match.group(1)}%"

        if "failed" in output_lower or "error" in output_lower:
            return "0% (testes falhando)"
        elif "passed" in output_lower or "ok" in output_lower:
            return "~10-30% (execução OK, cobertura não medida)"

        return "Não detectada"

    def _gerar_recomendacoes(self, estrutura: str, frameworks: str) -> str:
        recomendacoes = []

        if "src/" in estrutura or "app/" in estrutura:
            recomendacoes.append("• Criar testes para classes em src/app")

        if "src/services" in estrutura or "src/service" in estrutura:
            recomendacoes.append("• Adicionar testes unitários para serviços")

        if "src/controllers" in estrutura or "src/controller" in estrutura:
            recomendacoes.append("• Testar controllers/endpoints")

        if "src/models" in estrutura or "model" in estrutura:
            recomendacoes.append("• Testar modelos e validações")

        if "src/utils" in estrutura or "utils" in estrutura:
            recomendacoes.append("• Testar funções utilitárias")

        if not recomendacoes:
            return "• Analisar arquivos fonte e criar testes para classes principais"

        return "\n".join(recomendacoes)

    def _projeto_e_legivel_para_testes(self, relatorio: str) -> bool:
        linguagem = self._extrair_linguagem(relatorio)
        if linguagem and linguagem != "Não detectada":
            return True
        return False

    def _extrair_linguagem(self, relatorio: str) -> str:
        if "Linguagem detectada:" in relatorio:
            inicio = relatorio.find("Linguagem detectada:") + len(
                "Linguagem detectada:"
            )
            fim = relatorio.find("Frameworks de teste:")
            return relatorio[inicio:fim].strip()
        return "Não detectada"

    def _extrair_frameworks(self, relatorio: str) -> str:
        if "Frameworks de teste:" in relatorio:
            inicio = relatorio.find("Frameworks de teste:") + len(
                "Frameworks de teste:"
            )
            fim = relatorio.find("Pré-requisitos necessários:")
            if fim == -1:
                return relatorio[inicio:].strip()
            return relatorio[inicio:fim].strip()
        return "Não detectado"

    def _extrair_prerequisitos(self, relatorio: str) -> str:
        if "Pré-requisitos necessários:" in relatorio:
            inicio = relatorio.find("Pré-requisitos necessários:") + len(
                "Pré-requisitos necessários:"
            )
            return relatorio[inicio:].strip()
        return "Nenhum pré-requisito verificado"

    async def _continuar_execucao(self, user_id: int):
        contexto = self.contextos.get(user_id)
        if not contexto:
            return

        contexto.estado = TesteEstado.EXECUTANDO
        contexto.erro_encontrado = False

        await TelegramOutputHandler.send_response(
            contexto.chat_id, "🚀 **Iniciando implementação dos testes unitários...**"
        )

        contexto.progresso_task = asyncio.create_task(
            self._enviar_progresso_periodico(user_id)
        )

        try:
            await self._implementar_testes(contexto)

            if contexto.progresso_task and not contexto.progresso_task.done():
                contexto.progresso_task.cancel()

            await self._gerar_relatorio_final(user_id)

        except asyncio.CancelledError:
            await TelegramOutputHandler.send_response(
                contexto.chat_id, "❌ **Execução cancelada pelo usuário.**"
            )
        except Exception as e:
            logging.error(f"Erro na implementação: {e}")
            contexto.erro_encontrado = True
            await TelegramOutputHandler.send_response(
                contexto.chat_id, f"❌ **Erro durante implementação:** {str(e)}"
            )
        finally:
            if user_id in self.contextos:
                if contexto.progresso_task and not contexto.progresso_task.done():
                    contexto.progresso_task.cancel()
                del self.contextos[user_id]

    async def _enviar_progresso_periodico(self, user_id: int):
        contexto = self.contextos.get(user_id)
        if not contexto:
            return

        try:
            while True:
                await asyncio.sleep(120)

                if contexto.erro_encontrado or not contexto.start_time:
                    break

                tempo_decorrido = (datetime.now() - contexto.start_time).seconds // 60

                await TelegramOutputHandler.send_response(
                    contexto.chat_id,
                    f"⏳ **Em andamento há {tempo_decorrido} minutos...**\n\n"
                    "Os testes unitários ainda estão sendo implementados.\n"
                    "Aguarde mais um momento por favor.",
                )

        except asyncio.CancelledError:
            pass

    async def _implementar_testes(self, contexto: QATestContext):
        from core.tools.repository import ListDirectoryTool, ReadFileTool, WriteFileTool
        from core.tools.git_management import GitManagementTool
        from core.tools.skills import SkillActivationTool

        available_providers = await ProviderFactory.get_all_available_providers()
        if not available_providers:
            raise Exception("Nenhum provedor de IA disponível")

        tools = [
            ListDirectoryTool(),
            ReadFileTool(),
            WriteFileTool(),
            GitManagementTool(),
            SkillActivationTool(self.skill_loader),
        ]

        from core.tools.manager import ToolManager

        tool_manager = ToolManager(tools)

        tasks_md_path = os.path.join(
            settings.TMP_DIR, f"testes_{contexto.repo_name}.md"
        )

        system_prompt = f"""Você é o QAgent, especialista em QA e TESTES UNITÁRIOS.

Tarefa: Criar um plano de testes unitários e implementá-los.

CONTEXTO:
- Repositório: {contexto.repo_path}
- Estrutura: {contexto.estrutura}
- Frameworks: {contexto.frameworks}

PASSO 1 - PLANO:
Analise a estrutura do repositório e crie um arquivo .md com as tasks de testes a serem criadas.
O arquivo deve ser salvo em: {tasks_md_path}

Formato do arquivo .md:
# Plano de Testes Unitários

## Tasks de Teste
1. [ ] Testar classe X - método Y
2. [ ] Testar função Z

PASSO 2 - IMPLEMENTAÇÃO:
Após criar o arquivo .md, leia os arquivos fonte e crie os arquivos de teste unitário correspondentes.

PASSO 3 - EXECUÇÃO:
Execute os testes usando a ferramenta git_manage com action='run_tests'.

Ambiente: Windows
Base: {settings.BASE_DIR}
"""

        conversation_id = await MessageRepository.get_or_create_conversation(
            contexto.user_id
        )
        self.active_provider = available_providers[0]

        loop = AgentLoop(
            conversation_id,
            self.active_provider,
            tool_manager=tool_manager,
        )

        user_input = f"""Crie testes unitários para o repositório {contexto.repo_path}

Estrutura detectada:
{contexto.estrutura}

Frameworks detectados:
{contexto.frameworks}

1. Primeiro, crie um arquivo .md com o plano de testes em: {tasks_md_path}
2. Depois, implemente os testes conforme o plano
3. Execute os testes e retorne o resultado
"""

        await loop.run(user_input, system_prompt)

    async def _gerar_relatorio_final(self, user_id: int):
        contexto = self.contextos.get(user_id)
        if not contexto:
            return

        from core.tools.git_management import GitManagementTool

        git_tool = GitManagementTool()
        resultado_testes = await git_tool.execute(
            action="run_tests", repo_path=contexto.repo_path
        )

        cobertura_final = self._extrair_cobertura(resultado_testes)
        contexto.cobertura_final = cobertura_final

        tempo_total = 0
        if contexto.start_time:
            tempo_total = (datetime.now() - contexto.start_time).seconds // 60

        tasks_md_path = os.path.join(
            settings.TMP_DIR, f"testes_{contexto.repo_name}.md"
        )
        tasks_info = ""
        if os.path.exists(tasks_md_path):
            with open(tasks_md_path, "r", encoding="utf-8") as f:
                tasks_info = f.read()[:500]

        relatorio = f"""✅ **TESTES UNITÁRIOS CONCLUÍDOS**

━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ **Nome do Projeto:** {contexto.repo_name}

📊 **Cobertura Inicial:** {contexto.cobertura_inicial}

📈 **Cobertura Final:** {contexto.cobertura_final}

⏱️ **Tempo Total:** {tempo_total} minutos

📝 **Resumo do que foi feito:**
• Análise da estrutura do repositório
• Detecção de frameworks de teste
• Criação do plano de testes ({tasks_md_path})
• Implementação dos testes unitários
• Execução e validação dos testes

📁 **Arquivos criados em:** {contexto.repo_path}

━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Os testes foram implementados conforme o plano criado.
"""

        await TelegramOutputHandler.send_response(contexto.chat_id, relatorio)

        contexto.estado = TesteEstado.FINALIZADO

    async def _cancelar_execucao(self, user_id: int, message: types.Message):
        if user_id in self.contextos:
            contexto = self.contextos[user_id]
            if contexto.progresso_task and not contexto.progresso_task.done():
                contexto.progresso_task.cancel()
            del self.contextos[user_id]

        await message.reply("❌ **Operação cancelada.**")

    async def handle_callback(self, callback: types.CallbackQuery):
        await callback.answer()
        user_id = callback.from_user.id
        data = callback.data

        if data == "confirmar_testes":
            await callback.message.edit_text(
                "✅ **Confirmado! Iniciando implementação...**"
            )
            await self._continuar_execucao(user_id)
        elif data == "cancelar_testes":
            await callback.message.edit_text("❌ **Operação cancelada.**")
            if user_id in self.contextos:
                contexto = self.contextos[user_id]
                if contexto.progresso_task and not contexto.progresso_task.done():
                    contexto.progresso_task.cancel()
                del self.contextos[user_id]
        else:
            await callback.message.edit_text(
                "ℹ️ Use o comando com 'Teste Unitário' + link .git para iniciar."
            )
