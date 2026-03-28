import logging
from typing import List, Dict, Any, Optional
from core.provider import BaseProvider, ProviderFactory
from memory.repository import MessageRepository
from core.config import settings

class AgentLoop:
    def __init__(self, conversation_id: str, provider: BaseProvider):
        self.conversation_id = conversation_id
        self.provider = provider
        self.max_iterations = settings.MAX_ITERATIONS

    async def run(self, user_input: str, system_prompt: str = "Você é o QAgent, um assistente técnico de QA.") -> str:
        """Executa o ciclo ReAct para processar a entrada do usuário."""
        
        # 1. Salvar mensagem do usuário
        await MessageRepository.add_message(self.conversation_id, "user", user_input)
        
        # 2. Recuperar histórico (incluindo a mensagem recém salva)
        history = await MessageRepository.get_messages(self.conversation_id, limit=settings.MEMORY_WINDOW_SIZE)
        
        # 3. Preparar o contexto completo (System + History)
        messages = [{"role": "system", "content": system_prompt}] + history
        
        current_iteration = 0
        final_answer = ""
        
        while current_iteration < self.max_iterations:
            current_iteration += 1
            logging.info(f"Iniciando Iteração {current_iteration}/{self.max_iterations}")
            
            # 4. Solicitar inferência ao Provedor
            response_content = await self.provider.generate_response(messages)
            
            # 5. Analisar se é uma Resposta Final ou Tool Call (Simplificado para o MVP)
            # No futuro, aqui entra o parser de Tool Calls do ReAct
            if "FINAL_ANSWER" in response_content or current_iteration == self.max_iterations:
                final_answer = response_content.replace("FINAL_ANSWER:", "").strip()
                break
            
            # Simulação de PENSAMENTO (Thought)
            logging.info(f"Pensamento do Agente: {response_content[:100]}...")
            
            # Se não houver ferramentas disponíveis, assumimos que a resposta é final
            # (Nesta versão base, ainda não temos o motor de busca de tools injetado)
            final_answer = response_content
            break

        # 6. Salvar e retornar resposta final
        await MessageRepository.add_message(self.conversation_id, "assistant", final_answer)
        return final_answer
