import os
import sys
import asyncio
from dotenv import load_dotenv

# Configuração de path antes dos imports do projeto
sys.path.append(os.getcwd())
load_dotenv()

from core.controller import AgentController  # noqa: E402
from core.loop import AgentLoop  # noqa: E402
from core.tools.repository import ListDirectoryTool, ReadFileTool, WriteFileTool  # noqa: E402
from core.tools.git_management import GitManagementTool  # noqa: E402
from core.tools.skills import SkillActivationTool  # noqa: E402
from core.tools.log_tool import UpdateLogTool  # noqa: E402
from core.tools.manager import ToolManager  # noqa: E402

async def simulate():
    print("Iniciando simulacao de controller (Apenas o começo para ver o primeiro Thought)...")
    controller = AgentController()
    await controller.initialize()
    
    provider = controller.provider_service.get_primary_provider()
    
    
    # Preparar ferramentas
    
    tools = [
        ListDirectoryTool(),
        ReadFileTool(),
        WriteFileTool(),
        GitManagementTool(),
        SkillActivationTool(controller.skill_loader),
        UpdateLogTool(),
    ]
    tool_manager = ToolManager(tools)

    skills_prompt = controller._get_skills_prompt()

    system_prompt = f"""Você é o QAgent, especialista em QA e TESTES UNITÁRIOS.

{skills_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    REGRAS DE AUDITORIA (OBRIGATÓRIO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. REGRA ZERO: Você NÃO PODE realizar nenhuma ação sem antes registrar seu pensamento em 'log.md'.
2. Use a ferramenta 'update_log' no INÍCIO de cada iteração.
3. Se você esquecer de registrar no log, a tarefa será considerada FALHA.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    OBJETIVO DA TAREFA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tarefa: Criar um plano de testes unitários e implementá-los usando as Ferramentas fornecidas.
"""
    print("--------------------------------------------------")
    print("Enviando requisição (limitada a 1 loop) para a LLM...")
    
    # We pass a print-based status callback to see what happens
    async def status_cb(msg):
        print(f"[STATUS] {msg}")
        
    loop = AgentLoop("test-123", provider, tool_manager, status_cb, [provider])
    loop.max_iterations = 2 
    
    try:
        await loop.run("iniciar testes no projeto flask", system_prompt)
    except Exception as e:
        print(f"Loop finalizado com erro/exception: {e}")
        
    print("\n--- Verifica se log.md foi criado ---")
    if os.path.exists("projects/flask/log.md"):
        print("SIM! O log foi criado.")
        with open("projects/flask/log.md", "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("NÃO! Log não foi criado.")

if __name__ == "__main__":
    asyncio.run(simulate())
