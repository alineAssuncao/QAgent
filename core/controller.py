import logging
import os
import asyncio
import shutil
import re
import json
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
from core.tools.repository import ReadFileTool, WriteFileTool
from aiogram import types
import sys


class TesteEstado(Enum):
    ANALISE = "analise"
    AGUARDANDO_CONFIRMACAO = "aguardando_confirmacao"
    EXECUTANDO = "executando"
    GERACAO_DASHBOARD = "geracao_dashboard"
    FINALIZADO = "finalizado"


# Mapeamento de palavras-chave para tipo de teste
TEST_TYPE_KEYWORDS = {
    "unitario": ["unit[aáàã]rio", "unitário", "unit test"],
    "integracao": ["integra[cç][aã]o", "integration test", "testar m[oó]dulos"],
    "api": ["testar api", "endpoint", "rest", "graphql", "contract"],
    "frontend": [
        "frontend",
        "componente",
        "react test",
        "vue test",
        "playwright",
        "cypress",
        "testar ui",
    ],
    "analise": [
        "analisar c[oó]digo",
        "code review",
        "qualidade",
        "code smell",
        "complexidade",
    ],
    "relatorio": ["relat[oó]rio", "dashboard", "m[eé]tricas", "cobertura"],
    "refatorar": ["refatorar", "testabilidade", "refactoring", "desacoplar"],
    "cicd": ["pipeline", "ci/cd", "github actions", "gitlab ci"],
    "documentar": [
        "documentar teste",
        "plano de teste",
        "test plan",
        "bdd",
        "gherkin",
        "rastreabilidade",
    ],
}

# Keywords genéricos que ativam o QA Maestro (qualquer tipo de teste)
QA_KEYWORDS = [
    r"teste",
    r"test",
    r"testar",
    r"cobertura",
    r"coverage",
    r"qualidade",
    r"quality",
    r"automa[cç][aã]o",
    r"analisar",
    r"relat[oó]rio",
    r"refatorar",
    r"pipeline",
    r"documentar",
    r"plano de teste",
]


class QATestContext:
    def __init__(self):
        self.estado: TesteEstado = TesteEstado.ANALISE
        self.user_id: int = 0
        self.chat_id: int = 0
        self.status_msg_id: Optional[int] = (
            None  # Mensagem de status dinâmico que será editada
        )
        self.lifecycle: Dict[str, str] = {
            "clonagem": "⏳",
            "analise": "⏳",
            "medicao_inicial": "⏳",
            "implementacao": "⏳",
            "dashboard": "⏳",
            "conclusao": "⏳",
        }
        self.repo_name: str = ""
        self.repo_path: str = ""
        # ... (restante igual, mas vou manter os novos campos de log que inseri antes)
        self.git_url: Optional[str] = None
        self.test_type: str = "unitario"
        self.cobertura_inicial: str = "0%"
        self.cobertura_final: str = "0%"
        self.resultado_testes_antes_bruto: str = ""
        self.resultado_testes_depois_bruto: str = ""
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
        has_qa_keyword = any(re.search(kw, lower_input) for kw in QA_KEYWORDS)

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
                message,
                git_url=git_url,
                local_path=None,
                requires_audio=requires_audio,
                test_type=test_type,
            )
        elif has_local_path:
            await self._iniciar_fluxo_qa(
                message,
                git_url=None,
                local_path=local_path,
                requires_audio=requires_audio,
                test_type=test_type,
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
            # Iniciando o Card de Status (Checklist Global)
            card_inicial = await self._renderizar_card_status(contexto)
            status_msg = await message.reply(card_inicial)
            contexto.status_msg_id = status_msg.message_id

            if git_url:
                await self._set_step_status(user_id, "clonagem", "🔄")
                from core.tools.git import CloneRepositoryTool

                clone_tool = CloneRepositoryTool()
                await clone_tool.execute(url=git_url)
                await self._set_step_status(user_id, "clonagem", "✅")
                contexto.repo_name = git_url.split("/")[-1].replace(".git", "")
                contexto.repo_path = f"projects/{contexto.repo_name}"
                from core.bot import bot

                await bot.send_message(
                    chat_id,
                    f"✅ <b>Repositório clonado:</b> {contexto.repo_name}",
                    parse_mode="HTML",
                )
            else:
                await self._set_step_status(user_id, "clonagem", "✅")
                contexto.repo_name = local_path or "unknown"
                contexto.repo_path = f"projects/{contexto.repo_name}"
                from core.bot import bot

                await bot.send_message(
                    chat_id,
                    f"✅ <b>Usando repositório local:</b> {contexto.repo_name}",
                    parse_mode="HTML",
                )

            await self._analisar_repositorio(contexto, user_id, message)

        except Exception as e:
            logging.error(f"Erro no fluxo de teste unitário: {e}")
            await self._set_step_status(user_id, "clonagem", "❌")
            await TelegramOutputHandler.send_response(
                chat_id, f"❌ **Erro:** {str(e)}", parse_mode="HTML"
            )
            if user_id in self.contextos:
                del self.contextos[user_id]

    async def _renderizar_card_status(self, contexto: QATestContext) -> str:
        """Gera a representação textual do Lifecycle Card."""
        l = contexto.lifecycle
        return f"""📋 <b>Status de Automação: QAgent</b>
━━━━━━━━━━━━━━━━━━━━
{l["clonagem"]} 📥 <b>Clonagem do Repositório</b>
{l["analise"]} 🔍 <b>Análise de Estrutura</b>
{l["medicao_inicial"]} 📊 <b>Medição de Cobertura Inicial</b>
{l["implementacao"]} 🛠️ <b>Implementação de Testes</b>
{l["dashboard"]} 🎨 <b>Geração do Dashboard Analítico</b>
{l["conclusao"]} ✅ <b>Conclusão e Relatório</b>
━━━━━━━━━━━━━━━━━━━━
_Acompanhe o progresso em tempo real._"""

    async def _set_step_status(self, user_id: int, step: str, status: str):
        """Atualiza um passo do lifecycle e edita o card no Telegram."""
        contexto = self.contextos.get(user_id)
        if not contexto or not contexto.chat_id:
            return

        contexto.lifecycle[step] = status
        card_texto = await self._renderizar_card_status(contexto)

        from core.bot import bot

        if contexto.status_msg_id:
            try:
                await bot.edit_message_text(
                    chat_id=contexto.chat_id,
                    message_id=contexto.status_msg_id,
                    text=card_texto,
                    parse_mode="HTML",
                )
                return
            except Exception as e:
                logging.warning(f"Não foi possível editar mensagem, enviando nova: {e}")

        try:
            new_msg = await bot.send_message(
                contexto.chat_id, card_texto, parse_mode="HTML"
            )
            contexto.status_msg_id = new_msg.message_id
        except Exception as e:
            logging.warning(f"Não foi possível enviar mensagem de status: {e}")

    async def _analisar_repositorio(
        self, contexto: QATestContext, user_id: int, message: types.Message
    ):
        from core.bot import bot
        from core.tools.repository import ListDirectoryTool
        from core.tools.git_management import GitManagementTool

        from core.tools.skills import SkillActivationTool

        try:
            await message.edit_text(
                "🔍 <b>Analisando estrutura do repositório...</b>", parse_mode="HTML"
            )
        except Exception as e:
            logging.warning(f"Não foi possível editar mensagem: {e}")
            await bot.send_message(
                contexto.chat_id,
                "🔍 <b>Analisando estrutura do repositório...</b>",
                parse_mode="HTML",
            )

        list_tool = ListDirectoryTool()
        estrutura = await list_tool.execute(path=contexto.repo_path)
        contexto.estrutura = estrutura

        try:
            await message.edit_text(
                "🛠️ <b>Detectando frameworks de teste...</b>", parse_mode="HTML"
            )
        except Exception as e:
            logging.warning(f"Não foi possível editar mensagem: {e}")
            await bot.send_message(
                contexto.chat_id,
                "🛠️ <b>Detectando frameworks de teste...</b>",
                parse_mode="HTML",
            )

        git_tool = GitManagementTool()
        frameworks = await git_tool.execute(
            action="detect_tests", repo_path=contexto.repo_path
        )
        contexto.frameworks = frameworks
        await self._set_step_status(user_id, "analise", "✅")

        if not self._projeto_e_legivel_para_testes(frameworks):
            await self._set_step_status(user_id, "analise", "❌")
            await TelegramOutputHandler.send_response(
                contexto.chat_id,
                f"""❌ <b>Projeto não elegível para testes unitários</b>

                ━━━━━━━━━━━━━━━━━━━━━━━━━━

                🏷️ <b>Projeto:</b> {contexto.repo_name}

                🗣️ <b>Linguagem detectada:</b> {self._extrair_linguagem(frameworks)}

                ⚠️ <b>Motivo:</b> O projeto não possui uma linguagem de programação detectada ou não possui arquivos fonte compatíveis com testes unitários automatizados.

                📝 <b>O que isso significa:</b>
                • O repositório pode não ter código fonte (apenas文档ação, configurações, etc.)
                • A linguagem utilizada pode não ser suportada para automação de testes unitários
                • Pode ser um projeto de infraestrutura, configuração ou sem código executável

                💡 <b>Sugestão:</b>
                • Verifique se o repositório contém código fonte
                • Considere usar testes de integração para este projeto
                • Este projeto pode precisar de abordagem manual de QA

                ━━━━━━━━━━━━━━━━━━━━━━━━━━
                """,
                parse_mode="HTML",
            )
            if user_id in self.contextos:
                del self.contextos[user_id]
            return

        try:
            await message.edit_text(
                "📊 <b>Executando testes atuais para medir cobertura...</b>",
                parse_mode="HTML",
            )
        except Exception as e:
            logging.warning(f"Não foi possível editar mensagem: {e}")
            await bot.send_message(
                contexto.chat_id,
                "📊 <b>Executando testes atuais para medir cobertura...</b>",
                parse_mode="HTML",
            )

        repo_full_path = os.path.join(settings.BASE_DIR, contexto.repo_path)

        has_tests = self._check_has_tests(repo_full_path)

        if has_tests:
            needs_install = self._check_needs_install(repo_full_path)
            if needs_install:
                logging.info(
                    f"[MEDICAO] Projeto precisa de instalação. Instalando dependências..."
                )
                install_result = await self._install_project_dependencies(
                    repo_full_path
                )
                if install_result:
                    logging.info(f"[MEDICAO] Instalação concluída com sucesso")
                else:
                    logging.warning(
                        f"[MEDICAO] Falha na instalação, tentando rodar mesmo assim"
                    )

            resultado_testes = await git_tool._run_command(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=.",
                    "--cov-report=term",
                    "--maxfail=5",
                ],
                cwd=repo_full_path,
            )
            resultado_testes_str = f"{'✅ Sucesso' if resultado_testes.returncode == 0 else '❌ Falha'}:\n{resultado_testes.stdout}\n{resultado_testes.stderr}"
        else:
            resultado_testes_str = (
                "Nenhum teste encontrado no projeto. Testes precisam ser criados."
            )

        contexto.resultado_testes_antes_bruto = resultado_testes_str

        cobertura = self._extrair_cobertura(resultado_testes_str)
        contexto.cobertura_inicial = cobertura

        contexto.recomendacoes = self._gerar_recomendacoes(estrutura, frameworks)

        await self._set_step_status(user_id, "medicao_inicial", "✅")

        relatorio = f"""📊 <b>RELATÓRIO DE ANÁLISE</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━

🏷️ <b>Nome do Projeto:</b> {contexto.repo_name}

📈 <b>Cobertura de Testes Atual:</b> {contexto.cobertura_inicial}

🗣️ <b>Linguagem de Programação:</b>
{self._extrair_linguagem(contexto.frameworks)}

🔧 <b>Ferramentas para Testes Unitários:</b>
{self._extrair_frameworks(contexto.frameworks)}

⚠️ <b>Pré-Requisitos Necessários:</b>
{self._extrair_prerequisitos(contexto.frameworks)}

💡 <b>O que pode ser melhorado para 100% de cobertura:</b>
{contexto.recomendacoes}

━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Iniciando a criação automática dos testes unitários...</b>
"""

        await TelegramOutputHandler.send_response(
            contexto.chat_id, relatorio, parse_mode="HTML"
        )

        await self._continuar_execucao(user_id)

    def _extrair_cobertura(self, output_testes: str) -> str:
        padroes_cobertura = [
            r"(\d+)%\s*coverage",
            r"coverage.*?(\d+)%",
            r"(\d+)%\s*covered",
            r"COVERAGE.*?(\d+)%",
            r"Total.*?(\d+)%",
            r"Branch.*?(\d+)%",
            r"TOTAL\s+\d+\s+\d+\s+(\d+)%",
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

    def _indicador(self, percentual: int) -> str:
        if percentual < 70:
            return "🔴"
        elif percentual < 85:
            return "🟡"
        else:
            return "🟢"

    def _extrair_resumo_coverage(self, texto: str) -> str:
        padrao = re.compile(
            r"^(?P<name>\S+\.py|TOTAL)\s+"
            r"(?P<stmts>\d+)\s+"
            r"(?P<miss>\d+)\s+"
            r"(?P<cover>\d+%)",
            re.MULTILINE,
        )

        resultados = padrao.findall(texto)

        if not resultados:
            return "⚠️ <b>Nenhuma informação de coverage encontrada.</b>"

        linhas = []
        total_info = None

        for name, stmts, miss, cover in resultados:
            percentual = int(cover.replace("%", ""))
            bolinha = self._indicador(percentual)
            barra = self.gerar_barra(percentual)

            if name == "TOTAL":
                total_info = (stmts, miss, cover, bolinha)
                continue

            linhas.append(
                f"{bolinha} <b>{name}</b>\n"
                f"Cobertura: {barra}\n"
                f"Total de linhas: {stmts}\n"
                f"Linhas não cobertas: {miss}\n"
            )

        mensagem = "<b>📊 Resumo de Cobertura</b>\n\n"
        mensagem += "\n".join(linhas)

        if total_info:
            stmts, miss, cover, bolinha = total_info
            percentual_total = int(cover.replace("%", ""))
            barra_total = self.gerar_barra(percentual_total)
            mensagem += (
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{bolinha} <b>COBERTURA GERAL</b>\n"
                f"Cobertura: {barra_total}\n"
                f"Total de linhas: {stmts}\n"
                f"Linhas não cobertas: {miss}"
            )

        return mensagem

    def gerar_barra(self, percentual: int) -> str:
        blocos_total = 8
        preenchidos = round((percentual / 100) * blocos_total)
        barra = "█" * preenchidos + "▒" * (blocos_total - preenchidos)
        return f"<code>[{barra}]</code> {percentual}%"

    def _carregar_dados_json_log(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Tenta carregar o arquivo de métricas JSON do projeto."""
        json_path = os.path.join(settings.BASE_DIR, repo_path, "qagent_metrics_log.json")
        if not os.path.exists(json_path):
            return None
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erro ao carregar qagent_metrics_log.json: {e}")
            return None

    def _gerar_resumo_visual_json(self, data: Dict[str, Any]) -> str:
        """Gera o resumo visual do Telegram usando dados estruturados do JSON."""
        breakdown = data.get("breakdown", [])
        coverage_data = data.get("coverage", {})
        coverage_total = coverage_data.get("after", 0)
        
        # Tenta pegar totais de linhas se disponíveis no root ou no breakdown
        total_stmts = 0
        total_miss = 0

        if not breakdown:
            return "⚠️ <b>Dados de coverage não encontrados no log estruturado.</b>"

        linhas = []
        for item in breakdown:
            name = item.get("module", "unknown")
            percentual = int(item.get("coverage_after", 0))
            stmts = item.get("stmts", 0)
            miss = item.get("miss", 0)
            
            total_stmts += stmts
            total_miss += miss
            
            bolinha = self._indicador(percentual)
            barra = self.gerar_barra(percentual)

            linhas.append(
                f"{bolinha} <b>{name}</b>\n"
                f"Cobertura: {barra}\n"
                f"Total de linhas: {stmts}\n"
                f"Linhas não cobertas: {miss}\n"
            )

        mensagem = "<b>📊 Resumo de Cobertura</b>\n\n"
        mensagem += "\n".join(linhas)

        # Adicionar Cobertura Geral
        bolinha_geral = self._indicador(int(coverage_total))
        barra_geral = self.gerar_barra(int(coverage_total))
        mensagem += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"{bolinha_geral} <b>COBERTURA GERAL</b>\n"
            f"Cobertura: {barra_geral}\n"
            f"Total de linhas: {total_stmts}\n"
            f"Linhas não cobertas: {total_miss}"
        )

        return mensagem

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
            contexto.chat_id,
            "🚀 <b>Iniciando implementação dos testes unitários...</b>",
            parse_mode="HTML",
        )

        contexto.progresso_task = asyncio.create_task(
            self._enviar_progresso_periodico(user_id)
        )

        try:
            await self._implementar_testes(contexto)
            await self._set_step_status(user_id, "implementacao", "✅")

            if contexto.progresso_task and not contexto.progresso_task.done():
                contexto.progresso_task.cancel()

            await self._gerar_relatorio_final(user_id)
            await self._set_step_status(user_id, "conclusao", "✅")

        except asyncio.CancelledError:
            await TelegramOutputHandler.send_response(
                contexto.chat_id,
                "❌ <b>Execução cancelada pelo usuário.</b>",
                parse_mode="HTML",
            )
        except Exception as e:
            logging.error(f"Erro na implementação: {e}")
            contexto.erro_encontrado = True

            erro_msg = str(e)
            if (
                "402" in erro_msg
                or "Payment Required" in erro_msg
                or "Insufficient Balance" in erro_msg
            ):
                mensagem_amigavel = """❌ <b>Ops! Problema de crédito</b>

━━━━━━━━━━━━━━━━━━━━
Seu crédito de API esgotou. Para continuar:

💳 <b>Opção 1:</b> Adicione créditos no DeepSeek
🌐 <b>Opção 2:</b> Configure outro provedor no .env
🔑 <b>Opção 3:</b> Verifique sua chave da API

━━━━━━━━━━━━━━━━━━━━
O teste foi cancelado por falta de crédito."""
            elif "429" in erro_msg or "Too Many Requests" in erro_msg:
                mensagem_amigavel = """❌ <b>Ops! Many requests</b>

━━━━━━━━━━━━━━━━━━━━
Os provedores de IA estão com limite excedido no momento.

⏱️ <b>Aguarde alguns minutos</b> e tente novamente.
━━━━━━━━━━━━━━━━━━━━
O teste foi cancelado temporariamente."""
            elif "RateLimitError" in erro_msg:
                mensagem_amigavel = """❌ <b>Limite de requisições atingido</b>

━━━━━━━━━━━━━━━━━━━━
Você atingiu o limite de requests. Aguarde um momento e tente novamente.

⏱️ <b>Dica:</b> O limite deve ser resetado em alguns minutos.
━━━━━━━━━━━━━━━━━━━━"""
            else:
                mensagem_amigavel = f"❌ <b>Erro durante implementação:</b> {str(e)}"

            await TelegramOutputHandler.send_response(
                contexto.chat_id,
                mensagem_amigavel,
                parse_mode="HTML",
            )
            raise e
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
                    f"⏳  <b>Em andamento há {tempo_decorrido} minutos...</b>\n\n"
                    "Os testes unitários ainda estão sendo implementados.\n"
                    "Aguarde mais um momento por favor.",
                    parse_mode="HTML",
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

                    Tarefa: Criar um plano de testes unitários e implementá-los usando as Ferramentas fornecidas.

    CHECKLIST ATUAL DO PROJETO:
    {contexto.lifecycle}

    CONTEXTO:
    - Repositório: {contexto.repo_path}
    - Estrutura: {contexto.estrutura}
    - Frameworks: {contexto.frameworks}   

                    REGRAS ESTritas:
                    1. Você NÃO PODE dar FINAL_ANSWER sem antes agir e usar as ferramentas.
                    2. Use a ferramenta 'list_directory' ou 'read_file' para entender os arquivos fonte.
                    3. Use a ferramenta 'write_file' para salvar os testes unitários.
                    4. Use a ferramenta 'git_manage' com action='run_tests' para validar os testes.

                    PASSO 1 - PLANO:
                    Crie um arquivo .md com as tasks de testes a serem criadas. Use a ferramenta 'write_file'.
                    Arquivo deve ser salvo em: {tasks_md_path}

                    Formato do arquivo .md:
                    # Plano de Testes Unitários

                    ## Tasks de Teste
                    1. [ ] Testar classe X - método Y
                    2. [ ] Testar função Z

                    PASSO 2 - IMPLEMENTAÇÃO:
                    Leia os arquivos fonte (read_file) e crie/salve os arquivos de teste correspondentes no diretório correto (write_file).

                    PASSO 3 - EXECUÇÃO:
                    Execute os testes usando a ferramenta 'git_manage' com action='run_tests'.
                    Apenas depois disso você pode responder com FINAL_ANSWER.

                    Ambiente: {"Windows" if sys.platform == "win32" else "Linux"}
                    Base: {settings.BASE_DIR}
                    """

        conversation_id = await MessageRepository.get_or_create_conversation(
            contexto.user_id
        )
        self.active_provider = available_providers[0]

        loop = AgentLoop(
            conversation_id=conversation_id,
            provider=self.active_provider,
            tool_manager=tool_manager,
            status_callback=lambda text: self._set_step_status(
                contexto.user_id, "implementacao", text
            ),
            available_providers=available_providers,
        )

        user_input = f"""ATIVIDADE CRÍTICA: OBRIGATÓRIO COMPLETAR O CICLO.

Crie testes unitários para o repositório {contexto.repo_path}. O caminho dos arquivos deve começar com {contexto.repo_path}.

1. Primeiro, USE 'write_file' para o plano: {tasks_md_path}
2. IMEDIATAMENTE DEPOIS, use 'read_file' em cascata para ler os fontes e 'write_file' para criar os testes em 'tests/'.
3. Por fim, USE 'git_manage' (run_tests) para validar e ver a cobertura real.

NÃO DÊ FINAL_ANSWER APENAS COM O PLANO. VOCÊ DEVE ESCREVER O CÓDIGO DOS TESTES AGORA. E SÓ PARE QUANDO OS TESTES ESTIVEREM PASSANDO.
"""

        await loop.run(user_input, system_prompt)

    async def _gerar_relatorio_final(self, user_id: int):
        import logging
        import subprocess

        contexto = self.contextos.get(user_id)
        if not contexto:
            return

        logging.info(f"[RELATORIO] Gerando relatorio para {contexto.repo_path}")

        from core.tools.git_management import GitManagementTool

        git_tool = GitManagementTool()
        resultado_testes = await git_tool.execute(
            action="run_tests", repo_path=contexto.repo_path
        )

        resumo = self._extrair_resumo_coverage(resultado_testes)

        repo_full_path = os.path.join(settings.BASE_DIR, contexto.repo_path)

        logging.info(f"[RELATORIO] Verificando estrutura de testes em {repo_full_path}")

        has_tests = self._check_has_tests(repo_full_path)
        logging.info(f"[RELATORIO] Has tests: {has_tests}")

        if not has_tests:
            logging.info(
                f"[RELATORIO] Nenhum teste encontrado. O agente deve criar os testes."
            )
            contexto.cobertura_final = "0% (testes a serem criados)"
        else:
            logging.info(
                f"[RELATORIO] Executando testes diretamente em {repo_full_path}"
            )

            needs_install = self._check_needs_install(repo_full_path)
            if needs_install:
                logging.info(
                    f"[RELATORIO] Projeto precisa de instalação. Instalando dependências..."
                )
                install_result = await self._install_project_dependencies(
                    repo_full_path
                )
                if install_result:
                    logging.info(f"[RELATORIO] Instalação concluída")
                else:
                    logging.warning(
                        f"[RELATORIO] Falha na instalação, tentando rodar mesmo assim"
                    )

            try:
                result = await git_tool._run_command(
                    [
                        "python",
                        "-m",
                        "pytest",
                        "--cov=.",
                        "--cov-report=term",
                        "--maxfail=5",
                    ],
                    cwd=repo_full_path,
                )
                resultado_testes = f"{'✅ Sucesso' if result.returncode == 0 else '❌ Falha'}:\n{result.stdout}\n{result.stderr}"
            except Exception as e:
                logging.warning(f"[RELATORIO] Erro ao executar testes: {e}")
                resultado_testes = f"Erro: {str(e)}"

            logging.info(
                f"[RELATORIO] resultado_testes: {resultado_testes[:500] if resultado_testes else 'VAZIO'}"
            )

            contexto.resultado_testes_depois_bruto = resultado_testes

            cobertura_final = self._extrair_cobertura(resultado_testes)
            logging.info(f"[RELATORIO] cobertura_final extraida: {cobertura_final}")
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
                tasks_info = f.read()

        caminho_relatorio_projeto = os.path.join(
            settings.BASE_DIR, contexto.repo_path, "relatorio_testes_qagent.md"
        )
        conteudo_relatorio = f"""# Relatório de Testes Automatizados - QAgent

**Projeto:** {contexto.repo_name}
**Data:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Tempo de Execução:** {tempo_total} minutos

## Resultado de Cobertura
- **Cobertura Inicial:** {contexto.cobertura_inicial}
- **Cobertura Final:** {contexto.cobertura_final}

                                ## Plano de Testes Executado (Resumo de Tasks)
                                {tasks_info}
                                """
        try:
            with open(caminho_relatorio_projeto, "w", encoding="utf-8") as f:
                f.write(conteudo_relatorio)
        except Exception as e:
            logging.error(f"Erro ao salvar o relatório dentro do projeto: {e}")

        # Geração do Dashboard Visual
        try:
            await self._set_step_status(user_id, "dashboard", "🔄")
            await self._gerar_dashboard(contexto, tempo_total)
            await self._set_step_status(user_id, "dashboard", "✅")
        except Exception as e:
            logging.error(f"Erro na fase de geração do Dashboard: {e}")
            await self._set_step_status(user_id, "dashboard", "❌")

        # Tenta carregar dados do JSON para um relatório visual superior
        json_data = self._carregar_dados_json_log(contexto.repo_path)
        if json_data:
            resumo = self._gerar_resumo_visual_json(json_data)
        else:
            resumo = self._extrair_resumo_coverage(contexto.resultado_testes_depois_bruto)

        relatorio = f"""✅ <b>TESTES UNITÁRIOS CONCLUÍDOS</b>

━━━━━━━━━━━━━━━━━━━━

🏷️ <b>Nome do Projeto:</b> {contexto.repo_name}

{resumo}

━━━━━━━━━━━━━━━━━━━━

⏱️ <b>Tempo Total:</b> {tempo_total} minutos

📝 <b>Resumo do que foi feito:</b>
• Análise da estrutura do repositório
• Detecção de frameworks de teste
• Implementação dos testes unitários
• Execução e validação dos testes

📑 <b>Relatório detalhado exportado em:</b>
<code>{contexto.repo_path}/relatorio_testes_qagent.md</code>

📁 <b>Arquivos de código criados em:</b>
<code>{contexto.repo_path}</code>

━━━━━━━━━━━━━━━━━━━━

💡 <i>Os testes foram implementados conforme o plano e o registro salvo no projeto.</i>
"""

        await TelegramOutputHandler.send_response(
            contexto.chat_id, relatorio, parse_mode="HTML"
        )

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

    async def _gerar_dashboard(self, contexto: QATestContext, tempo_total: int):
        import uuid
        import logging
        from core.config import settings

        logging.info(f"[DASHBOARD] Gerando dashboard para {contexto.repo_path}")
        logging.info(f"[DASHBOARD] cobertura_inicial: {contexto.cobertura_inicial}")
        logging.info(f"[DASHBOARD] cobertura_final: {contexto.cobertura_final}")
        logging.info(
            f"[DASHBOARD] resultado_testes (primeiros 500 chars): {str(contexto.resultado_testes_depois_bruto)[:500] if contexto.resultado_testes_depois_bruto else 'VAZIO'}"
        )

        template_path = os.path.join(
            settings.BASE_DIR, "assets", "qa_dashboard_template.html"
        )
        output_path = os.path.join(
            settings.BASE_DIR, contexto.repo_path, "qa_coverage_dashboard.html"
        )
        json_log_path = os.path.join(
            settings.BASE_DIR, contexto.repo_path, "qagent_metrics_log.json"
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        coverage_before = self._parse_coverage(contexto.cobertura_inicial)
        coverage_after = self._parse_coverage(contexto.cobertura_final)

        tests_info = self._parse_test_logs(contexto.resultado_testes_depois_bruto)
        logging.info(f"[DASHBOARD] tests_info parsed: {tests_info}")

        log_coverage = tests_info.get("coverage", 0.0)

        if log_coverage > 0:
            coverage_after = log_coverage
        elif (
            coverage_after == 0
            and "pytest" in contexto.resultado_testes_depois_bruto.lower()
        ):
            coverage_after = 30.0

        # Refatorado para usar o log real do antes para o breakdown
        breakdown = self._parse_coverage_breakdown(
            contexto.resultado_testes_depois_bruto,
            contexto.resultado_testes_antes_bruto,
            coverage_before, 
            coverage_after
        )

        history_trend = {
            "labels": [],
            "cov_before": [],
            "cov_after": [],
            "tests_exec": [],
            "tests_fail": [],
            "gen_time": [],
            "exec_time": [],
        }
        json_log_path = os.path.join(
            settings.BASE_DIR, contexto.repo_path, "qagent_metrics_log.json"
        )
        if os.path.exists(json_log_path):
            try:
                with open(json_log_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    history_trend = existing_data.get("history_trend", history_trend)
            except Exception as e:
                logging.warning(f"Erro ao ler metrics anterior: {e}")

        temp_qa_data = {
            "coverage": {
                "before": coverage_before,
                "after": coverage_after,
            },
            "tests": {
                "total_executed": tests_info.get("executed", 0),
                "failures": tests_info.get("failed", 0),
                "passed": tests_info.get("passed", 0),
            },
            "performance": {
                "generation_time_seconds": tempo_total * 60,
                "execution_time_seconds": tempo_total * 60,
            },
        }
        distribution = self._generate_distribution(temp_qa_data, breakdown)

        qa_data = {
            "metadata": {
                "run_id": f"QA-RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "branch": contexto.repo_name,
            },
            "coverage": {
                "before": coverage_before,
                "after": coverage_after,
                "delta_absolute": round(coverage_after - coverage_before, 2),
                "delta_percentual": round(
                    ((coverage_after - coverage_before) / max(coverage_before, 1))
                    * 100,
                    2,
                ),
            },
            "tests": {
                "total_created": tests_info.get("total", 0),
                "total_executed": tests_info.get("executed", 0),
                "failures": tests_info.get("failed", 0),
                "passed": tests_info.get("passed", 0),
            },
            "performance": {
                "generation_time_seconds": tempo_total * 60,
                "execution_time_seconds": tempo_total * 60,
            },
            "breakdown": breakdown,
            "distribution": distribution,
            "insights": {
                "en": [
                    self._generate_insight_en(
                        tests_info, coverage_before, coverage_after
                    )
                ],
                "pt": [
                    self._generate_insight_pt(
                        tests_info, coverage_before, coverage_after
                    )
                ],
            },
            "history_trend": history_trend,
        }

        new_history = self._update_history_trend(history_trend, qa_data)
        qa_data["history_trend"] = new_history

        with open(json_log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(qa_data, indent=2, ensure_ascii=False))

        html_content = self._inject_qa_data_into_html(template_content, qa_data)
        logging.info(f"[DASHBOARD] HTML injetado, tamanho: {len(html_content)}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logging.info(f"[DASHBOARD] Arquivo salvo em: {output_path}")

    def _parse_coverage(self, coverage_str: str) -> float:
        match = re.search(r"(\d+(?:\.\d+)?)", str(coverage_str))
        return float(match.group(1)) if match else 0.0

    def _generate_insight_en(
        self, tests_info: dict, cov_before: float, cov_after: float
    ) -> str:
        passed = tests_info.get("passed", 0)
        failed = tests_info.get("failed", 0)
        total = tests_info.get("total_created", 0)

        if failed > 0:
            return f"Test suite executed: {passed} passed, {failed} failed out of {total} tests. Coverage: {cov_after}%"
        elif passed > 0:
            return f"All {passed} tests passed successfully. Coverage improved from {cov_before}% to {cov_after}%"
        else:
            return f"Test generation completed. {total} test cases created. Note: Test execution may need manual verification."

    def _generate_insight_pt(
        self, tests_info: dict, cov_before: float, cov_after: float
    ) -> str:
        passed = tests_info.get("passed", 0)
        failed = tests_info.get("failed", 0)
        total = tests_info.get("total_created", 0)

        if failed > 0:
            return f"Suite de testes executada: {passed} passaram, {failed} falharam de {total} testes. Cobertura: {cov_after}%"
        elif passed > 0:
            return f"Todos os {passed} testes passaram com sucesso. Cobertura melhorou de {cov_before}% para {cov_after}%"
        else:
            return f"Geração de testes concluída. {total} casos de teste criados. Nota: Execução pode precisar de verificação manual."

    def _parse_test_logs(self, logs: str) -> dict:
        total = len(re.findall(r"test_", logs))
        failed = len(re.findall(r"FAILED|ERROR|FAIL", logs, re.IGNORECASE))

        passed_match = re.findall(r"(\d+) failed.*?(\d+) passed", logs, re.IGNORECASE)
        if passed_match:
            failed = int(passed_match[0][0])
            passed = int(passed_match[0][1])
        else:
            passed_match = re.findall(r"(\d+) passed", logs, re.IGNORECASE)
            passed = int(passed_match[0]) if passed_match else 0
            if passed == 0 and "passed" in logs.lower():
                passed = len(re.findall(r"PASSED", logs))

        coverage_match = re.search(
            r"(\d+)%\s*(?:coverage|covered)", logs, re.IGNORECASE
        )
        if not coverage_match:
            coverage_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", logs)
        coverage = float(coverage_match.group(1)) if coverage_match else 0.0

        return {
            "total": total,
            "executed": passed + failed,
            "failed": failed,
            "passed": passed,
            "coverage": coverage,
        }

    async def _load_history_trend(
        self, read_tool: ReadFileTool, output_path: str
    ) -> dict:
        try:
            existing = await read_tool.execute(path=output_path)
            match = re.search(r"const __QA_DATA__ = ({.*?});", existing, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                return data.get(
                    "history_trend",
                    {
                        "labels": [],
                        "cov_before": [],
                        "cov_after": [],
                        "tests_exec": [],
                        "tests_fail": [],
                        "gen_time": [],
                        "exec_time": [],
                    },
                )
        except:
            pass
        return {
            "labels": [],
            "cov_before": [],
            "cov_after": [],
            "tests_exec": [],
            "tests_fail": [],
            "gen_time": [],
            "exec_time": [],
        }

    def _update_history_trend(self, history: dict, qa_data: dict) -> dict:
        import uuid

        label = f"Run {uuid.uuid4().hex[:4]}"
        history["labels"].append(label)
        history["cov_before"].append(qa_data["coverage"]["before"])
        history["cov_after"].append(qa_data["coverage"]["after"])
        history["tests_exec"].append(qa_data["tests"]["total_executed"])
        history["tests_fail"].append(qa_data["tests"]["failures"])
        history["gen_time"].append(qa_data["performance"]["generation_time_seconds"])
        history["exec_time"].append(qa_data["performance"]["execution_time_seconds"])
        return history

    def _inject_qa_data_into_html(self, template: str, qa_data: dict) -> str:
        json_str = json.dumps(qa_data, indent=4, ensure_ascii=False)

        start_marker = "const __QA_DATA__ = "
        start_idx = template.find(start_marker)
        if start_idx == -1:
            return template

        end_marker = "};"
        search_start = start_idx + len(start_marker)
        end_idx = template.find(end_marker, search_start)

        if end_idx == -1:
            return template

        new_content = f"{start_marker}{json_str};"
        result = (
            template[:start_idx] + new_content + template[end_idx + len(end_marker) :]
        )

        return result

    def _check_has_tests(self, repo_path: str) -> bool:
        """Verifica se o repositório tem arquivos de teste."""
        import os

        if not os.path.exists(repo_path):
            return False

        for root, dirs, files in os.walk(repo_path):
            if ".git" in root or "__pycache__" in root:
                continue

            for f in files:
                if f.startswith("test_") and f.endswith(".py"):
                    return True
                if f.endswith("_test.py"):
                    return True

            if "tests" in dirs:
                tests_dir = os.path.join(root, "tests")
                if os.path.isdir(tests_dir):
                    for f in os.listdir(tests_dir):
                        if f.endswith(".py"):
                            return True

        return False

    def _get_coverage_map(self, output_testes: str) -> Dict[str, float]:
        """Extrai um mapeamento de arquivo -> coverage de um log do pytest."""
        cov_map = {}
        if not output_testes:
            return cov_map

        lines = output_testes.split("\n")
        for line in lines:
            line = line.strip()
            if (
                line
                and not line.startswith("=")
                and not line.startswith("TOTAL")
                and not line.startswith("Name")
            ):
                parts = line.split()
                if len(parts) >= 4:
                    first_col = parts[0]
                    if (
                        first_col.endswith(".py")
                        or "/" in first_col
                        or "\\" in first_col
                    ):
                        try:
                            module = first_col.replace("\\", "/")
                            coverage_str = parts[3].replace("%", "").replace(",", "")
                            if coverage_str.replace(".", "").replace("-", "").isdigit():
                                cov_map[module] = float(coverage_str)
                        except:
                            pass
        return cov_map

    def _parse_coverage_breakdown(
        self, output_testes: str, output_antes: str = "", coverage_before_total: float = 0, coverage_after_total: float = 0
    ) -> list:
        """Parseia a cobertura por módulo do output do pytest, comparando com o antes real."""
        breakdown = []
        
        # Mapear cobertura inicial real se disponível
        antes_map = self._get_coverage_map(output_antes)

        lines = output_testes.split("\n")
        for line in lines:
            line = line.strip()
            if (
                line
                and not line.startswith("=")
                and not line.startswith("TOTAL")
                and not line.startswith("Name")
            ):
                parts = line.split()
                if len(parts) >= 4:
                    first_col = parts[0]
                    if (
                        first_col.endswith(".py")
                        or "/" in first_col
                        or "\\" in first_col
                    ):
                        try:
                            module = first_col.replace("\\", "/")
                            stmts = int(parts[1]) if parts[1].isdigit() else 0
                            miss = int(parts[2]) if parts[2].isdigit() else 0
                            coverage = parts[3].replace("%", "").replace(",", "")
                            
                            if coverage.replace(".", "").replace("-", "").isdigit():
                                cov_float = min(float(coverage), 100.0)
                                # Buscar cobertura real "antes" de cada arquivo
                                cov_before = antes_map.get(module, 0.0)
                                delta = round(cov_float - cov_before, 2)

                                breakdown.append(
                                    {
                                        "module": module,
                                        "stmts": stmts,
                                        "miss": miss,
                                        "coverage_before": round(cov_before, 2),
                                        "coverage_after": round(cov_float, 2),
                                        "delta": delta,
                                    }
                                )
                        except:
                            pass

        if not breakdown and coverage_after_total > 0:
            breakdown.append(
                {
                    "module": "Main Module (project)",
                    "coverage_before": coverage_before_total,
                    "coverage_after": coverage_after_total,
                    "delta": round(coverage_after_total - coverage_before_total, 2),
                }
            )

        return sorted(breakdown, key=lambda x: x["delta"], reverse=True)[:10]

    def _check_has_tests(self, repo_path: str) -> bool:
        """Verifica se o repositório tem arquivos de teste."""
        import os

        if not os.path.exists(repo_path):
            return False

        for root, dirs, files in os.walk(repo_path):
            if ".git" in root or "__pycache__" in root:
                continue

            for f in files:
                if f.startswith("test_") and f.endswith(".py"):
                    return True
                if f.endswith("_test.py"):
                    return True

            if "tests" in dirs:
                tests_dir = os.path.join(root, "tests")
                if os.path.isdir(tests_dir):
                    for f in os.listdir(tests_dir):
                        if f.endswith(".py"):
                            return True

        return False

    def _check_needs_install(self, repo_path: str) -> bool:
        """Verifica se o projeto precisa de instalação (tem setup.py, pyproject.toml, etc)."""
        import os

        install_indicators = [
            os.path.join(repo_path, "setup.py"),
            os.path.join(repo_path, "pyproject.toml"),
            os.path.join(repo_path, "setup.cfg"),
            os.path.join(repo_path, "requirements.txt"),
        ]

        for indicator in install_indicators:
            if os.path.exists(indicator):
                return True
        return False

    async def _install_project_dependencies(self, repo_path: str) -> bool:
        """Instala as dependências do projeto."""
        import os
        from core.tools.git_management import GitManagementTool

        git_tool = GitManagementTool()

        if os.path.exists(os.path.join(repo_path, "pyproject.toml")):
            result = await git_tool._run_command(
                ["python", "-m", "pip", "install", "-e", "."],
                cwd=repo_path,
            )
            logging.info(f"[INSTALL] pip install -e . result: {result.returncode}")
            return result.returncode == 0

        if os.path.exists(os.path.join(repo_path, "setup.py")):
            result = await git_tool._run_command(
                ["python", "-m", "pip", "install", "-e", "."],
                cwd=repo_path,
            )
            logging.info(f"[INSTALL] pip install -e . result: {result.returncode}")
            return result.returncode == 0

        if os.path.exists(os.path.join(repo_path, "requirements.txt")):
            result = await git_tool._run_command(
                ["python", "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=repo_path,
            )
            logging.info(
                f"[INSTALL] pip install -r requirements.txt result: {result.returncode}"
            )
            return result.returncode == 0

        return False

    def _generate_distribution(self, qa_data: dict, breakdown: list) -> dict:
        """Gera os dados de distribuição para os gráficos donut."""
        coverage = qa_data.get("coverage", {})
        tests = qa_data.get("tests", {})
        performance = qa_data.get("performance", {})

        cov_after = coverage.get("after", 0)
        cov_before = coverage.get("before", 0)

        total_exec = tests.get("total_executed", 0)
        failures = tests.get("failures", 0)
        passed = tests.get("passed", 0)

        gen_time = performance.get("generation_time_seconds", 0)
        exec_time = performance.get("execution_time_seconds", 0)

        return {
            "coverage_impact": {
                "covered": cov_after,
                "uncovered": max(0, 100 - cov_after),
                "before": cov_before,
            },
            "test_execution": {
                "passed": passed,
                "failed": failures,
                "skipped": max(0, total_exec - passed - failures),
            },
            "agent_performance": {
                "generation": gen_time,
                "execution": exec_time,
                "other": max(0, 100 - (gen_time + exec_time)),
            },
        }
