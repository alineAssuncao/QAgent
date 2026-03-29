import asyncio
import logging
import sys
import os

# Adicionar o diretório atual ao sys.path para importar os módulos locais
sys.path.append(os.getcwd())

from core.loop import AgentLoop
from core.provider import ProviderFactory
from core.tools.repository import ListDirectoryTool, ReadFileTool
from core.tools.skills import SkillActivationTool
from core.tools.manager import ToolManager
from skills.loader import SkillLoader
from memory.database import Database
from core.config import settings

async def test_loop():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # 1. Inicializar DB e Loader
    await Database.init_db()
    loader = SkillLoader(skills_dir=settings.SKILLS_DIR)
    loader.load_all_skills()
    
    # 2. Configurar Ferramentas
    tools = [
        ListDirectoryTool(),
        ReadFileTool(),
        SkillActivationTool(loader)
    ]
    tool_manager = ToolManager(tools)
    
    # 3. Obter Provedor (LM Studio se disponível)
    try:
        provider = await ProviderFactory.get_active_provider()
        logging.info(f"Usando provedor: {provider.name}")
    except Exception as e:
        logging.error(f"Erro ao obter provedor: {e}")
        return

    # 4. Configurar Loop
    conversation_id = "test_conversation"
    loop = AgentLoop(conversation_id, provider, tool_manager=tool_manager)
    
    # 5. Executar um teste que force o uso de ferramentas
    user_input = "Liste os arquivos na raiz do projeto e me diga o que o arquivo main.py faz."
    system_prompt = "Você é o QAgent, um assistente técnico de QA."
    
    print(f"\n[Usuário]: {user_input}")
    print("-" * 30)
    
    try:
        response = await loop.run(user_input, system_prompt)
        print(f"\n[QAgent]: {response}")
    except Exception as e:
        print(f"\n[ERRO]: {e}")
    finally:
        await Database.close()

if __name__ == "__main__":
    asyncio.run(test_loop())
