import logging
import json
import re
from typing import List, Dict, Any, Optional, Callable, Coroutine, Union
from core.provider import BaseProvider, RateLimitError
from memory.repository import MessageRepository
from core.config import settings
from core.tools.manager import ToolManager
from core.middleware import provider_health


class AgentLoop:
    def __init__(
        self,
        conversation_id: str,
        provider: BaseProvider,
        tool_manager: Optional[ToolManager] = None,
        status_callback: Optional[Callable[[str], Coroutine[Any, Any, None]]] = None,
        available_providers: List[BaseProvider] = None,
    ) -> None:
        self.conversation_id: str = conversation_id
        self.provider: BaseProvider = provider  # Provedor atual
        self.available_providers: List[BaseProvider] = available_providers or [provider]
        self.tool_manager: Optional[ToolManager] = tool_manager

        self.max_iterations: int = settings.MAX_ITERATIONS
        self.status_callback: Optional[Callable[[str], Coroutine[Any, Any, None]]] = (
            status_callback
        )

    @property
    def current_provider_name(self) -> str:
        """Retorna o nome do provedor sendo utilizado no momento."""
        return self.provider.name if self.provider else "Desconhecido"

    async def _update_status(self, text: str):
        """Helper para enviar atualizações de status via callback e log."""
        logging.info(f"[AGENT_STATUS] {text}")
        if self.status_callback:
            try:
                await self.status_callback(text)
            except Exception as e:
                logging.error(f"Erro ao enviar callback de status: {e}")

    async def run(self, user_input: str, system_prompt_base: str) -> str:
        """Executa o ciclo ReAct para processar a entrada do usuário."""

        # 1. Preparar Contexto de Ferramentas
        tools_str = (
            self.tool_manager.get_tool_definitions()
            if self.tool_manager
            else "Nenhuma ferramenta disponível."
        )

        react_instructions = f"""
Siga rigorosamente o formato de raciocínio ReAct:

Thought: Seu raciocínio sobre o que fazer a seguir.
Action: O nome da ferramenta a ser usada (deve ser uma das ferramentas listadas abaixo).
Action Input: Os argumentos para a ferramenta em formato JSON válido.
Observation: O resultado da ferramenta (será fornecido pelo sistema).
... (este ciclo Thought/Action/Action Input/Observation pode se repetir {self.max_iterations} vezes)
Thought: Eu agora sei a resposta final.
FINAL_ANSWER: Sua resposta final para o usuário em português.

Ferramentas Disponíveis:
{tools_str}

Lembre-se: Sempre use 'FINAL_ANSWER:' para concluir sua tarefa.
VOCÊ NÃO PODE GERAR O BLOCO 'Observation:'. O sistema fornecerá a observação após o seu 'Action Input:'. Pare de gerar texto imediatamente após 'Action Input:'.
"""
        system_prompt = f"{system_prompt_base}\n{react_instructions}"

        # 2. Salvar mensagem do usuário e carregar histórico
        await MessageRepository.add_message(self.conversation_id, "user", user_input)
        history = await MessageRepository.get_messages(
            self.conversation_id, limit=settings.MEMORY_WINDOW_SIZE
        )

        # Sanitizar histórico: remover alucinações de Observation: de mensagens do assistant
        sanitized_history = []
        for msg in history:
            content = msg["content"]
            if msg["role"] == "assistant" and "Observation:" in content:
                # Remove o bloco de observação e tudo depois dele na mensagem do assistant
                content = content.split("Observation:")[0].strip()
            sanitized_history.append({"role": msg["role"], "content": content})

        # O contexto inicial (System + Mensagens anteriores)
        messages = [{"role": "system", "content": system_prompt}] + sanitized_history

        current_iteration = 0
        final_answer = (
            "Desculpe, não consegui processar sua solicitação após várias tentativas."
        )

        await self._update_status("🧠 Iniciando processamento da solicitação...")

        while current_iteration < self.max_iterations:
            current_iteration += 1
            logging.info(
                f"\n{'=' * 20} Iteração {current_iteration}/{self.max_iterations} {'=' * 20}"
            )

            # 3. Solicitar inferência ao Provedor (com lógica de Fallback)
            response_content = None
            retries = 0
            max_fallback_retries = len(self.available_providers)

            while retries < max_fallback_retries:
                try:
                    response_content = await self.provider.generate_response(messages)
                    break
                except RateLimitError as e:
                    retries += 1
                    provider_health.mark_unhealthy(self.provider.name)

                    next_provider = None
                    for p in self.available_providers:
                        if p.name != self.provider.name and provider_health.is_healthy(
                            p.name
                        ):
                            next_provider = p
                            break

                    if next_provider:
                        msg_fallback = f"🔄 Limite atingido no {self.provider.name}. Alternando para {next_provider.name}..."
                        await self._update_status(msg_fallback)
                        self.provider = next_provider
                    else:
                        error_msg = f"❌ Limite de cota atingido em todos os provedores disponíveis."
                        await self._update_status(error_msg)
                        raise e
                except Exception as e:
                    error_str = str(e).lower()
                    retries += 1

                    is_retryable = any(
                        x in error_str
                        for x in [
                            "400",
                            "timeout",
                            "connection",
                            "failed to load",
                            "error loading model",
                            "server disconnected",
                            "unavailable",
                        ]
                    )

                    if is_retryable:
                        provider_health.mark_unhealthy(self.provider.name)
                        next_provider = None
                        for p in self.available_providers:
                            if (
                                p.name != self.provider.name
                                and provider_health.is_healthy(p.name)
                            ):
                                next_provider = p
                                break

                        if next_provider:
                            msg_fallback = f"⚠️ Erro no {self.provider.name}: {str(e)[:50]}... Alternando para {next_provider.name}..."
                            await self._update_status(msg_fallback)
                            self.provider = next_provider
                        else:
                            error_msg = f"❌ Erro em todos os provedores disponíveis: {str(e)[:100]}"
                            await self._update_status(error_msg)
                            raise e
                    else:
                        raise e

            if not response_content:
                raise Exception(
                    "Falha crítica: Provedor não retornou conteúdo após tentativas de fallback."
                )

            logging.info(
                f"[DEBUG] Resposta completa do modelo:\n{response_content[:1000]}..."
            )

            # 3.5 Prevenção de Alucinação: Truncar se o modelo tentar gerar sua própria Observation
            if "Observation:" in response_content:
                logging.warning("[AGENT_LOOP] Alucinação detectada: o modelo tentou gerar sua própria Observation. Truncando resposta.")
                response_content = response_content.split("Observation:")[0].strip()

            # Adicionar a resposta do assistente ao contexto do loop
            messages.append({"role": "assistant", "content": response_content})

            # 4. Verificar se é uma Resposta Final
            if "FINAL_ANSWER:" in response_content:
                # Verificar se o modelo executou ações antes do FINAL_ANSWER
                has_action_before_final = (
                    "Action:" in response_content.split("FINAL_ANSWER:")[0]
                )

                # Verificar se o modelo executou ações de escrita de código (não apenas .md)
                has_code_write = False
                for msg in messages:
                    if msg["role"] == "assistant" and "write_file" in msg["content"]:
                        # Se contiver write_file, verifica se não é apenas para arquivos .md ou logs
                        content = msg["content"].lower()
                        # Extrair o path do Action Input usando regex para ser mais preciso
                        path_matches = re.findall(r'"path":\s*"([^"]+)"', content)
                        for p in path_matches:
                            if not p.endswith(".md") and not p.endswith(".log") and not p.endswith(".txt"):
                                has_code_write = True
                                break
                    if has_code_write: break

                # No Agente Analista, não exigimos escrita de código REAL (.py)
                is_analyst = "AGENTE ANALISTA" in system_prompt_base
                
                # Analista: aceitar FINAL_ANSWER imediatamente (ele só lista arquivos)
                if is_analyst:
                    final_answer = response_content.split("FINAL_ANSWER:")[-1].strip()
                    await self._update_status("✅ Análise concluída.")
                    break
                
                # Coder/Tester: exigir que tenha executado ações E escrito código .py
                if not has_code_write and "test" in user_input.lower():
                    await self._update_status(
                        "⚠️ Implantação de código não detectada. Solicitando continuação..."
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": "ATIVIDADE CRÍTICA: OBRIGATÓRIO usar a ferramenta 'write_file' para criar o arquivo de testes .py FISICAMENTE antes de dar FINAL_ANSWER. NÃO apenas descreva o código, ESCREVA-O com write_file.",
                        }
                    )
                    continue

                final_answer = response_content.split("FINAL_ANSWER:")[-1].strip()
                await self._update_status("✅ Resposta final gerada.")
                break

            tool_name: str = "unknown"
            # 5. Tentar extrair Action e Action Input com Robustez
            try:
                action_match = re.search(r"Action:\s*(\w+)", response_content)
                action_input_match = re.search(
                    r"Action Input:\s*({.*})", response_content, re.DOTALL
                )

                if action_match and action_input_match and self.tool_manager:
                    tool_name = action_match.group(1).strip()
                    tool_args_str = action_input_match.group(1).strip()

                    try:
                        tool_args: Dict[str, Any] = json.loads(tool_args_str)
                    except json.JSONDecodeError:
                        decoder = json.JSONDecoder()
                        tool_args, _ = decoder.raw_decode(tool_args_str)

                    thought_match = re.search(
                        r"Thought:\s*(.*?)(?=Action:|$)", response_content, re.DOTALL
                    )
                    thought = (
                        thought_match.group(1).strip()
                        if thought_match
                        else "Analisando..."
                    )

                    await self._update_status(f"🛠️ Executando: {tool_name}")
                    logging.info(f"THOUGHT: {thought}")
                    logging.info(f"ACTION: {tool_name}({tool_args})")

                    observation = await self.tool_manager.call_tool(
                        tool_name, tool_args
                    )

                    obs_message = f"Observation: {observation}"
                    messages.append({"role": "user", "content": obs_message})
                    logging.info(f"OBSERVATION: {str(observation)[:200]}...")
                
                # FALLBACK: Tentar parsear JSON puro (modelo retornou {"action": "tool", ...})
                elif self.tool_manager:
                    json_parsed = False
                    # Limpar markdown code fences se existirem
                    clean = response_content.strip()
                    if clean.startswith("```"):
                        clean = re.sub(r"^```\w*\n?", "", clean)
                        clean = re.sub(r"\n?```$", "", clean).strip()
                    
                    try:
                        data = json.loads(clean)
                        if isinstance(data, dict) and "action" in data:
                            tool_name = data.pop("action")
                            # Remover campos duplicados/inválidos
                            tool_args = {k: v for k, v in data.items() if k != "action"}
                            
                            await self._update_status(f"🛠️ Executando: {tool_name}")
                            logging.info(f"[JSON-FALLBACK] ACTION: {tool_name}({tool_args})")

                            observation = await self.tool_manager.call_tool(
                                tool_name, tool_args
                            )

                            obs_message = f"Observation: {observation}"
                            messages.append({"role": "user", "content": obs_message})
                            logging.info(f"OBSERVATION: {str(observation)[:200]}...")
                            json_parsed = True
                    except (json.JSONDecodeError, TypeError):
                        pass
                    
                    if not json_parsed:
                        if current_iteration < self.max_iterations:
                            await self._update_status("🔄 Refinando raciocínio...")
                            messages.append(
                                {
                                    "role": "user",
                                    "content": "IMPORTANTE: Use EXATAMENTE este formato:\nThought: [seu raciocínio]\nAction: [nome_da_ferramenta]\nAction Input: {\"param\": \"valor\"}\n\nFerramentas: read_file, write_file, list_directory, git_manage",
                                }
                            )
                        else:
                            final_answer = response_content
                else:
                    if current_iteration < self.max_iterations:
                        messages.append(
                            {
                                "role": "user",
                                "content": "Por favor, continue usando o formato ReAct ou forneça a FINAL_ANSWER.",
                            }
                        )
                    else:
                        final_answer = response_content
            except Exception as e:
                error_msg = f"Erro ao processar ação: {str(e)}"
                await self._update_status(f"⚠️ Erro na ação: {tool_name}")
                messages.append(
                    {
                        "role": "user",
                        "content": f"Observation: {error_msg}. Por favor, corrija o formato.",
                    }
                )
                logging.error(error_msg)

        # 8. Salvar mensagem final
        await MessageRepository.add_message(
            self.conversation_id, "assistant", final_answer
        )
        return final_answer
