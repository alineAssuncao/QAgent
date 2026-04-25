import os
import sys
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from core.controller import AgentController

async def test_skills_loading():
    print("Iniciando teste de carregamento de skills...")
    controller = AgentController()
    await controller.initialize()
    
    print(f"Skills carregadas no loader: {[s['name'] for s in controller.skill_loader.skills]}")
    
    prompt = controller._get_skills_prompt()
    if prompt:
        print("\n--- SKILLS PROMPT ---")
        print(prompt)
        print("--- END ---")
    else:
        print("\n[ERRO] Prompt de skills está VAZIO!")

if __name__ == "__main__":
    asyncio.run(test_skills_loading())
