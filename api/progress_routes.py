from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database.database import get_db
from schemas.progress import ProgressResponse
from anxiety_signals.engine import anxiety_signals_engine

router = APIRouter()

@router.get("/progress/{student_id}", response_model=ProgressResponse)
def get_student_progress(student_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive progress report for a student
    """
    try:
        # Get confidence score
        confidence_score = anxiety_signals_engine.calculate_confidence_score(db, student_id)
        
        # Calculate consistency days (days active in last 30 days)
        consistency_days = 0  # Placeholder - would implement proper calculation
        improvement_streak = 0  # Placeholder - would implement proper calculation
        
        # Get total goals completed
        from database.models import MicroGoal
        total_goals_completed = db.query(MicroGoal).filter(
            MicroGoal.student_id == student_id,
            MicroGoal.completed == True
        ).count()
        
        # Determine recent performance trend
        recent_performance_trend = "stable"  # Placeholder - would analyze data
        
        progress = ProgressResponse(
            student_id=student_id,
            confidence_score=confidence_score,
            consistency_days=consistency_days,
            improvement_streak=improvement_streak,
            total_goals_completed=total_goals_completed,
            recent_performance_trend=recent_performance_trend,
            last_updated=datetime.utcnow()
        )
        
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting progress report: {str(e)}")