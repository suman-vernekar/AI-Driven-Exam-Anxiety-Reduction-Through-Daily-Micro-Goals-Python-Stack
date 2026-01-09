from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database.database import get_db
from schemas.micro_goal import MicroGoalCreate, MicroGoalResponse
from database.models import MicroGoal
from micro_goals.engine import micro_goal_engine

router = APIRouter()

@router.post("/micro-goals/generate", response_model=List[MicroGoalResponse])
def generate_daily_micro_goals(student_id: int, db: Session = Depends(get_db)):
    """
    Generate 2-4 small, realistic daily goals for a student
    based on their syllabus and performance history
    """
    try:
        # Generate micro goals using the engine
        goals_data = micro_goal_engine.generate_daily_goals(db, student_id)
        
        # Save the generated goals to the database
        created_goals = []
        for goal_data in goals_data:
            db_goal = MicroGoal(
                student_id=goal_data.student_id,
                topic_id=goal_data.topic_id,
                goal_text=goal_data.goal_text,
                estimated_time=goal_data.estimated_time,
                priority=goal_data.priority
            )
            db.add(db_goal)
            db.commit()
            db.refresh(db_goal)
            created_goals.append(db_goal)
        
        return created_goals
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating micro goals: {str(e)}")

@router.get("/micro-goals/{student_id}", response_model=List[MicroGoalResponse])
def get_student_micro_goals(student_id: int, db: Session = Depends(get_db)):
    """
    Get all micro goals for a specific student
    """
    goals = db.query(MicroGoal).filter(MicroGoal.student_id == student_id).all()
    return goals

# Add endpoint for creating custom micro-goals
@router.post("/micro-goals", response_model=MicroGoalResponse)
def create_micro_goal(goal: MicroGoalCreate, db: Session = Depends(get_db)):
    """
    Create a custom micro goal
    """
    try:
        db_goal = MicroGoal(
            student_id=goal.student_id,
            topic_id=goal.topic_id,
            goal_text=goal.goal_text,
            estimated_time=goal.estimated_time,
            priority=goal.priority
        )
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        
        return db_goal
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating micro goal: {str(e)}")

@router.put("/micro-goals/{goal_id}/complete")
def mark_goal_complete(goal_id: int, db: Session = Depends(get_db)):
    """
    Mark a micro goal as completed
    """
    goal = db.query(MicroGoal).filter(MicroGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    goal.completed = True
    goal.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Goal marked as completed", "success": True}

@router.delete("/micro-goals/{goal_id}")
def delete_micro_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    Delete a micro goal
    """
    goal = db.query(MicroGoal).filter(MicroGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Goal deleted successfully", "success": True}