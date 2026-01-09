from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    email: str
    grade: str
    exam_type: str  # "board" or "competitive"

class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    grade: str
    exam_type: str
    created_at: datetime

    class Config:
        from_attributes = True

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

class ProgressResponse(BaseModel):
    student_id: int
    confidence_score: float
    consistency_days: int
    improvement_streak: int
    total_goals_completed: int
    recent_performance_trend: str  # "improving", "declining", "stable"
    last_updated: datetime