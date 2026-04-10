import asyncio
import sqlite3
import os

async def check_db():
    db_path = "data/qagent.db"
    if not os.path.exists(db_path):
        print(f"Banco não encontrado em {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Tabelas no Banco ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    
    print("\n--- Sub-tarefas (project_subtasks) ---")
    try:
        cursor.execute("SELECT * FROM project_subtasks LIMIT 10;")
        tasks = cursor.fetchall()
        for t in tasks:
            print(t)
    except Exception as e:
        print(f"Erro ao ler sub-tarefas: {e}")
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(check_db())
