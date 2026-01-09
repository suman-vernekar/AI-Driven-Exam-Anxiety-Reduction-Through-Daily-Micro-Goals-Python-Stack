from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MicroGoalCreate(BaseModel):
    student_id: int
    topic_id: int
    goal_text: str
    estimated_time: int  # in minutes
    priority: int  # 1-5 priority level

class MicroGoalResponse(BaseModel):
    id: int
    student_id: int
    topic_id: int
    goal_text: str
    estimated_time: int
    priority: int
    created_at: datetime
    completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True