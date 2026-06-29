from fastapi import APIRouter, HTTPException, UploadFile, File
from api.models import ChatRequest, ChatResponse, ErrorResponse
from core.provider import ProviderFactory
import os
import shutil
import logging
from core.config import settings
from faster_whisper import WhisperModel

router = APIRouter(prefix="/v1")

# Instância do Whisper carregada apenas uma vez (singleton)
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        logging.info("Carregando modelo Faster-Whisper para a API...")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    return _whisper_model

@router.post("/chat", response_model=ChatResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint de Chat utilizando o provedor de IA configurado.
    """
    try:
        provider = await ProviderFactory.get_active_provider()
    except Exception as e:
        logging.error(f"Erro ao obter provedor: {e}")
        raise HTTPException(status_code=500, detail="Nenhum provedor de IA disponível.")
        
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    try:
        response_text = await provider.generate_response(messages_dict)
        return ChatResponse(response=response_text, provider=provider.name)
    except Exception as e:
        logging.error(f"Erro ao gerar resposta no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transcribe", responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Endpoint para transcrição de áudio usando Whisper.
    """
    if not file.filename.endswith((".ogg", ".mp3", ".wav", ".m4a")):
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado. Envie áudio (.ogg, .mp3, .wav, .m4a).")
        
    try:
        model = get_whisper_model()
    except Exception as e:
        logging.error(f"Erro ao carregar modelo Whisper: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao carregar o modelo de transcrição.")
        
    if not os.path.exists(settings.TMP_DIR):
        os.makedirs(settings.TMP_DIR)
        
    local_path = os.path.join(settings.TMP_DIR, f"api_upload_{file.filename}")
    
    try:
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        segments, info = model.transcribe(local_path, beam_size=5)
        transcript = " ".join([segment.text for segment in segments])
        
        return {"transcription": transcript.strip()}
    except Exception as e:
        logging.error(f"Erro na transcrição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao transcrever áudio: {str(e)}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)
