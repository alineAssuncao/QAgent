from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    
class ChatResponse(BaseModel):
    response: str
    provider: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
