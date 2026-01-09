from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProgressResponse(BaseModel):
    student_id: int
    confidence_score: float
    consistency_days: int
    improvement_streak: int
    total_goals_completed: int
    recent_performance_trend: str  # "improving", "declining", "stable"
    last_updated: datetime