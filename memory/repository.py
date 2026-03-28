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
