from pydantic import BaseModel
from typing import List, Optional

class MemorySchema(BaseModel):
    user_id: str
    thread_id: str
    role: str
    content: str
    timestamp: Optional[str] = None

class PlanSchema(BaseModel):
    step: int # Step number in the plan
    name: str # Name of the step (e.g., "Analyze Thesis", "Improve Evidence")
    operations: List[str] # List of operations to perform in this step

class PlanOutputSchema(BaseModel):
    steps: List[PlanSchema]