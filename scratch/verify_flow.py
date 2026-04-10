import asyncio
import os
from core.tools.repository import WriteFileTool, ReadFileTool
from core.config import settings

async def verify_flow():
    print("--- Verificando Fluxo de Escrita/Leitura ---")
    repo_name = "python-simple-rest-api"
    test_path = f"projects/{repo_name}/tests/diagnostic_test.py"
    content = "def test_diag():\n    assert True\n"
    
    # 1. Testar Escrita
    write_tool = WriteFileTool()
    print(f"Tentando escrever em: {test_path}")
    result = await write_tool.execute(path=test_path, content=content)
    print(f"Resultado escrita: {result}")
    
    # 2. Verificar existência física
    abs_path = os.path.join(settings.BASE_DIR, test_path)
    if os.path.exists(abs_path):
        print(f"SUCESSO: Arquivo fisicamente criado em {abs_path}")
    else:
        print(f"FALHA: Arquivo no encontrado em {abs_path}")

    # 3. Testar Leitura
    read_tool = ReadFileTool()
    read_content = await read_tool.execute(path=test_path)
    if read_content == content:
        print("SUCESSO: Contedo lido coincide com o escrito.")
    else:
        print(f"FALHA: Contedo divergente. Lido: {read_content}")

if __name__ == "__main__":
    asyncio.run(verify_flow())
