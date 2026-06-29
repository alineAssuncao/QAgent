import pytest
import asyncio
from core.bot import bot
from memory.database import Database

@pytest.fixture(scope="session", autouse=True)
async def cleanup_after_tests():
    """Garante que todas as conexões sejam fechadas após a suíte de testes."""
    yield
    # Lógica de encerramento após todos os testes
    print("\n[CONTEST] Iniciando limpeza de conexões pendentes...")
    
    try:
        if hasattr(bot, 'session') and bot.session and not bot.session.closed:
            await bot.session.close()
            print("[CONTEST] Sessão do Bot fechada com sucesso.")
    except Exception as e:
        print(f"[CONTEST] Erro ao fechar sessão do Bot: {e}")

    try:
        await Database.close()
        print("[CONTEST] Conexão com banco de dados fechada.")
    except Exception as e:
        print(f"[CONTEST] Erro ao fechar banco de dados: {e}")
