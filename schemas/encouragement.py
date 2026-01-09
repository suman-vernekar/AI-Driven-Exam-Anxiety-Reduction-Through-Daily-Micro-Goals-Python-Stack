from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

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