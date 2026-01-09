from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

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

class TopicCreate(BaseModel):
    name: str
    subject: str
    syllabus_id: int
    difficulty_level: str  # "easy", "medium", "hard"
    estimated_time: int  # in minutes

class TopicResponse(BaseModel):
    id: int
    name: str
    subject: str
    syllabus_id: int
    difficulty_level: str
    estimated_time: int

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

class AnxietySignalType(str, Enum):
    stress = "stress"
    improvement_streak = "improvement_streak"
    consistency = "consistency"
    effort_outcome_ratio = "effort_outcome_ratio"

class AnxietySignalCreate(BaseModel):
    student_id: int
    signal_type: AnxietySignalType
    value: float
    description: str

class AnxietySignalResponse(BaseModel):
    id: int
    student_id: int
    signal_type: AnxietySignalType
    value: float
    description: str
    detected_at: datetime

    class Config:
        from_attributes = True

class EncouragementType(str, Enum):
    daily = "daily"
    after_goal = "after_goal"
    consolation = "consolation"
    improvement = "improvement"

class EncouragementCreate(BaseModel):
    student_id: int
    message: str
    message_type: EncouragementType

class EncouragementResponse(BaseModel):
    id: int
    student_id: int
    message: str
    message_type: EncouragementType
    created_at: datetime
    viewed: bool

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