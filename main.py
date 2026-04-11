import asyncio
import logging
import sys

# Corrige o erro inútil do Windows Proactor (__del__) aparecendo ao fechar o servidor
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _original_del = _ProactorBasePipeTransport.__del__
        def _silenced_del(self):
            try:
                _original_del(self)
            except Exception:
                pass
        _ProactorBasePipeTransport.__del__ = _silenced_del
    except Exception:
        pass

from core.bot import dp, bot, setup_middlewares
from memory.database import Database

async def on_startup():
    """Lógica de inicialização do sistema."""
    logging.info("QAgent: Inicializando componentes...")
    await Database.init_db()

async def on_shutdown():
    """Lógica de encerramento seguro."""
    logging.info("QAgent: Encerrando conexões...")
    await Database.close()
    await bot.session.close()

async def main():
    # Registrar Handlers e Middlewares
    setup_middlewares(dp)
    
    # Hooks de ciclo de vida
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Iniciar polling assíncrono
    logging.info("Bot QAgent pronto para operação.")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Falha fatal no loop do bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Encerramento solicitado pelo usuário.")
        sys.exit(0)
