import asyncio
import logging
import sys
import os

# Adicionar o diretório atual ao sys.path para importar os módulos locais
sys.path.append(os.getcwd())

from core.loop import AgentLoop
from core.provider import ProviderFactory
from core.tools.repository import ListDirectoryTool, ReadFileTool
from core.tools.git import CloneRepositoryTool
from core.tools.manager import ToolManager
from core.config import settings
from memory.database import Database

async def test_git_clone():
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
    
    # 1. Configurar Provedor
    try:
        provider = await ProviderFactory.get_active_provider()
    except Exception as e:
        print(f"Erro ao obter provedor: {e}")
        return

    # 2. Configurar Ferramentas (Simulando o Controller)
    os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
    tools = [
        ListDirectoryTool(),
        ReadFileTool(),
        CloneRepositoryTool()
    ]
    tool_manager = ToolManager(tools)

    # 3. Iniciar Loop
    conversation_id = "test_git_clone"
    loop = AgentLoop(conversation_id, provider, tool_manager=tool_manager)
    
    # Repositório de teste (pequeno)
    test_url = "https://github.com/octocat/Spoon-Knife.git"
    user_input = f"Clone o repositório {test_url} e depois liste o que tem dentro dele."
    
    print(f"\n[USER]: {user_input}")
    print("-" * 30)
    
    try:
        await Database.init_db()
        response = await loop.run(user_input, "Você é o QAgent.")
        print(f"\n[AGENT]: {response}")
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(test_git_clone())
