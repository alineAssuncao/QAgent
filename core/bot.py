import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from core.config import settings

# Configuração de Logs
logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

# Instância do Bot e Dispatcher
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Instância do Controller (Lazy-loaded no main)
controller = None

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("🚀 **QAgent Online!**\nSou seu orquestrador de QA e Automação.\n\nEnvie texto, áudio ou PDF para começar.")

@router.message(F.from_user.id.in_(settings.allowed_user_ids))
async def handle_all_messages(message: types.Message):
    """Fallback para todas as mensagens (Se o ID estiver na Whitelist)."""
    global controller
    if not controller:
        from core.controller import AgentController
        controller = AgentController()
        await controller.initialize()
    
    await controller.handle_message(message)

@router.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    """Gerencia cliques em botões inline."""
    global controller
    if not controller:
        from core.controller import AgentController
        controller = AgentController()
        await controller.initialize()
    
    await controller.handle_callback(callback_query)

def setup_middlewares(dp: Dispatcher):
    # Middlewares de segurança e log podem ser injetados aqui
    dp.include_router(router)
    logging.info("Handlers e Routers registrados no Dispatcher.")
