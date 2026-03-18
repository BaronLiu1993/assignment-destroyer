from pydantic import BaseModel
from typing import List, Optional

class MemorySchema(BaseModel):
    user_id: str
    thread_id: str
    role: str
    content: str
    timestamp: Optional[str] = None