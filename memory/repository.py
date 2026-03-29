import logging
import uuid
from typing import List, Dict, Optional
from memory.database import Database

class MessageRepository:
    @staticmethod
    async def get_or_create_conversation(user_id: int, provider: str = "gemini") -> str:
        db = await Database.get_instance()
        cursor = await db.execute(
            "SELECT id FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return row[0]
        
        # Criar nova conversa se não existir
        new_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO conversations (id, user_id, provider) VALUES (?, ?, ?)",
            (new_id, user_id, provider)
        )
        await db.commit()
        logging.info(f"Nova conversa criada para usuário {user_id}: {new_id}")
        return new_id

    @staticmethod
    async def add_message(conversation_id: str, role: str, content: str):
        db = await Database.get_instance()
        await db.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        await db.commit()

    @staticmethod
    async def get_messages(conversation_id: str, limit: int = 10) -> List[Dict[str, str]]:
        db = await Database.get_instance()
        cursor = await db.execute(
            "SELECT role, content FROM (SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT ?) ORDER BY timestamp ASC",
            (conversation_id, limit)
        )
        rows = await cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]

    # --- Métodos de Gestão de Tarefas (Fila) ---

    @staticmethod
    async def get_active_task(user_id: int) -> Optional[Dict[str, Any]]:
        """Retorna a tarefa que está atualmente em execução para o usuário."""
        db = await Database.get_instance()
        cursor = await db.execute(
            "SELECT id, status, input_text FROM tasks WHERE user_id = ? AND status = 'running' LIMIT 1",
            (user_id,)
        )
        row = await cursor.fetchone()
        return {"id": row[0], "status": row[1], "input_text": row[2]} if row else None

    @staticmethod
    async def add_task(user_id: int, input_text: str, conversation_id: str = None, status: str = 'pending') -> int:
        """Adiciona uma nova tarefa à fila ou define como em execução."""
        db = await Database.get_instance()
        cursor = await db.execute(
            "INSERT INTO tasks (user_id, input_text, conversation_id, status) VALUES (?, ?, ?, ?) RETURNING id",
            (user_id, input_text, conversation_id, status)
        )
        row = await cursor.fetchone()
        await db.commit()
        return row[0]

    @staticmethod
    async def update_task_status(task_id: int, status: str):
        """Atualiza o status de uma tarefa (completed, cancelled, running)."""
        db = await Database.get_instance()
        await db.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        await db.commit()

    @staticmethod
    async def get_queue_size(user_id: int) -> int:
        """Retorna a quantidade de tarefas pendentes na fila."""
        db = await Database.get_instance()
        cursor = await db.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'", (user_id,))
        row = await cursor.fetchone()
        return row[0]

    @staticmethod
    async def clear_queue(user_id: int):
        """Remove todas as tarefas pendentes da fila."""
        db = await Database.get_instance()
        await db.execute("UPDATE tasks SET status = 'cancelled' WHERE user_id = ? AND status = 'pending'", (user_id,))
        await db.commit()

    @staticmethod
    async def pop_next_task(user_id: int) -> Optional[Dict[str, Any]]:
        """Busca a próxima tarefa pendente para iniciar."""
        db = await Database.get_instance()
        cursor = await db.execute(
            "SELECT id, input_text FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY created_at ASC LIMIT 1",
            (user_id,)
        )
        row = await cursor.fetchone()
        return {"id": row[0], "input_text": row[1]} if row else None
    @staticmethod
    async def update_task_plan(task_id: int, plan: str):
        """Atualiza o resumo/plano das sub-tarefas de uma task."""
        db = await Database.get_instance()
        await db.execute("UPDATE tasks SET tasks_planned = ? WHERE id = ?", (plan, task_id))
        await db.commit()

    @staticmethod
    async def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
        """Retorna os detalhes de uma tarefa específica."""
        db = await Database.get_instance()
        cursor = await db.execute("SELECT id, user_id, input_text, tasks_planned FROM tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()
        return {"id": row[0], "user_id": row[1], "input_text": row[2], "tasks_planned": row[3]} if row else None

    @staticmethod
    async def get_pending_tasks(user_id: int) -> List[Dict[str, Any]]:
        """Retorna todas as tarefas pendentes na fila para o usuário."""
        db = await Database.get_instance()
        cursor = await db.execute(
            "SELECT id, input_text, created_at FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY created_at ASC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [{"id": row[0], "input_text": row[1], "created_at": row[2]} for row in rows]
