from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class AnxietySignalType(str, Enum):
    stress = "stress"
    improvement_streak = "improvement_streak"
    consistency = "consistency"
    effort_outcome_ratio = "effort_outcome_ratio"
    confidence = "confidence"

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