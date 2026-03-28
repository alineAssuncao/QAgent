import logging
import os
import asyncio
from aiogram import types
from aiogram.utils.chat_action import ChatActionSender
from core.bot import bot
from core.config import settings
import edge_tts

class TelegramOutputHandler:
    @staticmethod
    async def send_response(chat_id: int, text: str, requires_audio: bool = False):
        """Define a melhor estratégia de envio (Texto ou Áudio/Voz)."""
        
        if requires_audio:
            await TelegramOutputHandler._send_voice(chat_id, text)
        else:
            await TelegramOutputHandler._send_text_chunks(chat_id, text)

    @staticmethod
    async def _send_text_chunks(chat_id: int, text: str):
        """Divide o texto em chunks de 4096 caracteres para respeitar o limite do Telegram."""
        limit = 4096
        for i in range(0, len(text), limit):
            chunk = text[i:i+limit]
            await bot.send_message(chat_id, chunk)
            # Pequeno delay para evitar Rate Limiting se houver muitos chunks
            if len(text) > limit:
                await asyncio.sleep(0.5)

    @staticmethod
    async def _send_voice(chat_id: int, text: str):
        """Gera áudio via Edge-TTS e envia como mensagem de voz."""
        tmp_path = os.path.join(settings.TMP_DIR, f"voice_{chat_id}.ogg")
        
        # Garantir diretório tmp
        if not os.path.exists(settings.TMP_DIR):
            os.makedirs(settings.TMP_DIR)

        try:
            async with ChatActionSender.record_voice(chat_id=chat_id, bot=bot):
                # Limpar markdown básico do texto para a voz não ler símbolos
                clean_text = text.replace("#", "").replace("*", "").replace("`", "")
                
                communicate = edge_tts.Communicate(clean_text, "pt-BR-ThalitaNeural")
                await communicate.save(tmp_path)
                
                # Enviar áudio
                voice = types.FSInputFile(tmp_path)
                await bot.send_voice(chat_id, voice)
        except Exception as e:
            logging.error(f"Erro ao gerar/enviar voz: {e}")
            await bot.send_message(chat_id, "⚠️ Não consegui gerar a resposta em áudio. Segue o texto:\n\n" + text)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @staticmethod
    async def send_document(chat_id: int, file_path: str, caption: str = ""):
        """Envia um arquivo local como documento."""
        if os.path.exists(file_path):
            doc = types.FSInputFile(file_path)
            await bot.send_document(chat_id, doc, caption=caption)
        else:
            logging.error(f"Arquivo não encontrado para envio: {file_path}")
