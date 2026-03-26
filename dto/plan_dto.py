from pydantic import BaseModel
from typing import List, Optional

class MemorySchema(BaseModel):
    user_id: str
    thread_id: str
    role: str
    content: str
    timestamp: Optional[str] = None

class StepSchema(BaseModel):
    plan_title: str
    plan_description: str

class PlanOutputSchema(BaseModel):
    plans: list[StepSchema]
    