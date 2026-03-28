import logging
import os
import aiohttp
from aiogram import types
from core.bot import bot
from core.config import settings
from faster_whisper import WhisperModel
import fitz # PyMuPDF

class TelegramInputHandler:
    # Modelo do Whisper carregado apenas quando necessário para economizar RAM
    _stt_model = None

    @classmethod
    def get_stt_model(cls):
        if cls._stt_model is None:
            logging.info("Carregando modelo Faster-Whisper...")
            cls._stt_model = WhisperModel("base", device="cpu", compute_type="int8")
        return cls._stt_model

    @staticmethod
    async def process_voice(message: types.Message) -> str:
        """Processa mensagens de voz e retorna transcrição STT."""
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Garantir diretório tmp
        if not os.path.exists(settings.TMP_DIR):
            os.makedirs(settings.TMP_DIR)
        
        local_path = os.path.join(settings.TMP_DIR, f"voice_{message.from_user.id}.ogg")
        await bot.download_file(file_path, local_path)
        
        try:
            model = TelegramInputHandler.get_stt_model()
            segments, info = model.transcribe(local_path, beam_size=5)
            transcript = " ".join([segment.text for segment in segments])
            logging.info(f"Transcrição Completa: {transcript}")
            return transcript.strip()
        except Exception as e:
            logging.error(f"Erro no Whisper STT: {e}")
            return "⚠️ Falha ao processar áudio localmente."
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)

    @staticmethod
    async def process_pdf(message: types.Message) -> str:
        """Processa documentos PDF e extrai o texto."""
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        local_path = os.path.join(settings.TMP_DIR, f"doc_{message.from_user.id}.pdf")
        await bot.download_file(file_path, local_path)
        
        try:
            doc = fitz.open(local_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return f"\n--- Conteúdo do PDF ({message.document.file_name}) ---\n{text}\n--- Fim do PDF ---\n"
        except Exception as e:
            logging.error(f"Erro ao ler PDF: {e}")
            return f"⚠️ Falha ao extrair texto do PDF {message.document.file_name}."
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
