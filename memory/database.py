import aiosqlite
import os
import logging
from core.config import settings

class Database:
    _instance = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            # Garantir que a pasta 'data' existe
            db_dir = os.path.dirname(settings.DATABASE_PATH)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logging.info(f"Diretório de dados criado: {db_dir}")

            cls._instance = await aiosqlite.connect(settings.DATABASE_PATH)
            # Ativar WAL mode para melhor performance concorrente
            await cls._instance.execute("PRAGMA journal_mode=WAL")
            await cls.init_db()
        return cls._instance

    @classmethod
    async def init_db(cls):
        db = await cls.get_instance()
        
        # Tabela de Conversas
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                provider TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Mensagens
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)

        # Tabela de Tarefas Principal
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT,
                status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'cancelled'
                input_text TEXT NOT NULL,
                tasks_planned TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de Sub-tarefas do Projeto (Fila de Orquestração)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS project_subtasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_task_id INTEGER NOT NULL,
                module_path TEXT NOT NULL,
                type TEXT NOT NULL, -- 'analise', 'codificacao', 'teste', 'verificacao'
                status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
                result_log TEXT,
                retry_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_task_id) REFERENCES tasks (id)
            )
        """)
        
        await db.commit()
        logging.info("Banco de Dados inicializado e tabelas verificadas.")

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
            logging.info("Conexão com Banco de Dados encerrada.")
