import logging
import json
import re
from typing import List, Dict, Any, Optional, Callable, Coroutine, Union
from core.provider import BaseProvider
from memory.repository import MessageRepository
from core.config import settings
from core.tools.manager import ToolManager


class AgentLoop:
    def __init__(
        self,
        conversation_id: str,
        provider: BaseProvider,
        tool_manager: Optional[ToolManager] = None,
        status_callback: Optional[Callable[[str], Coroutine[Any, Any, None]]] = None,
    ) -> None:
        self.conversation_id: str = conversation_id
        self.provider: BaseProvider = provider
        self.tool_manager: Optional[ToolManager] = tool_manager
        self.max_iterations: int = settings.MAX_ITERATIONS
        self.status_callback: Optional[Callable[[str], Coroutine[Any, Any, None]]] = (
            status_callback
        )

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
"""
        system_prompt = f"{system_prompt_base}\n{react_instructions}"

        # 2. Salvar mensagem do usuário e carregar histórico
        await MessageRepository.add_message(self.conversation_id, "user", user_input)
        history = await MessageRepository.get_messages(
            self.conversation_id, limit=settings.MEMORY_WINDOW_SIZE
        )

        # O contexto inicial (System + Mensagens anteriores)
        messages = [{"role": "system", "content": system_prompt}] + history

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

            # 3. Solicitar inferência ao Provedor
            response_content = await self.provider.generate_response(messages)

            # Adicionar a resposta do assistente ao contexto do loop
            messages.append({"role": "assistant", "content": response_content})

            # 4. Verificar se é uma Resposta Final
            if "FINAL_ANSWER:" in response_content:
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
                else:
                    if current_iteration < self.max_iterations:
                        await self._update_status("🔄 Refinando raciocínio...")
                        messages.append(
                            {
                                "role": "user",
                                "content": "Por favor, continue seu raciocínio usando o formato ReAct ou forneça a FINAL_ANSWER se já tiver concluído.",
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
