from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PerformanceRecordCreate(BaseModel):
    student_id: int
    topic_id: int
    score: float
    time_spent: int
    mistakes: Optional[str] = None
    completed: bool = True

class PerformanceRecordResponse(BaseModel):
    id: int
    student_id: int
    topic_id: int
    date: datetime
    score: float
    time_spent: int
    mistakes: Optional[str] = None
    completed: bool

    class Config:
        from_attributes = True