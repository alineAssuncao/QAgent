import logging
import os
from core.config import settings
from typing import Optional
from core.provider import ProviderFactory, BaseProvider
from core.loop import AgentLoop
from skills.loader import SkillLoader
from memory.repository import MessageRepository
from memory.database import Database
from handlers.input import TelegramInputHandler
from handlers.output import TelegramOutputHandler
from aiogram import types

class AgentController:
    def __init__(self):
        self.skill_loader = SkillLoader(skills_dir=settings.SKILLS_DIR)
        self.active_provider: Optional[BaseProvider] = None

    async def initialize(self):
        """Inicializa o banco de dados e as skills no startup."""
        await Database.init_db()
        self.skill_loader.load_all_skills()
        logging.info("AgentController inicializado.")

    async def handle_message(self, message: types.Message):
        """Ponto de entrada único para mensagens do Telegram."""
        user_id = message.from_user.id
        user_input = ""
        requires_audio = False
        
        # 1. Processar o Input (Texto, Voz ou PDF)
        if message.text:
            user_input = message.text
        elif message.voice or message.audio:
            user_input = await TelegramInputHandler.process_voice(message)
            requires_audio = True
        elif message.document:
            if message.document.file_name.endswith('.pdf'):
                user_input = await TelegramInputHandler.process_pdf(message)
                if message.caption:
                    user_input = f"{message.caption}\n{user_input}"
            else:
                await message.reply("⚠️ Atualmente só suporto PDFs e Áudio além de texto.")
                return

        if not user_input:
            return

        # 2. Obter ou Criar Conversa e Selecionar Provedor
        try:
            self.active_provider = await ProviderFactory.get_active_provider()
            conversation_id = await MessageRepository.get_or_create_conversation(user_id)
        except Exception as e:
            logging.error(f"Erro de Provedor/DB: {e}")
            await message.reply(f"❌ Erro Crítico: {e}")
            return

        # 3. Router de Skill (Passo Zero - Simplificado)
        # Por enquanto, injetamos todas as skills disponíveis ou um prompt básico
        # No futuro, o SkillRouter filtrará aqui
        system_prompt = "Você é o QAgent, um assistente de QA e Automação."
        all_skills = self.skill_loader.skills
        if all_skills:
            skills_context = "\n".join([f"- {s['name']}: {s['description']}" for s in all_skills])
            system_prompt += f"\nVocê tem acesso às seguintes habilidades:\n{skills_context}"

        # 4. Iniciar Engine de Raciocínio (Agent Loop)
        loop = AgentLoop(conversation_id, self.active_provider)
        
        # 5. Gerar Resposta
        try:
            # Sinalizar ao usuário que o Agente está pensando
            from core.bot import bot
            from aiogram.utils.chat_action import ChatActionSender
            
            async with ChatActionSender.typing(chat_id=message.chat.id, bot=bot):
                response = await loop.run(user_input, system_prompt)
            
            # 6. Enviar Resposta Final via OutputHandler
            await TelegramOutputHandler.send_response(message.chat.id, response, requires_audio=requires_audio)
            
        except Exception as e:
            logging.error(f"Erro no Agent Loop: {e}")
            await message.reply(f"⚠️ Ocorreu um erro no processamento: {e}")
