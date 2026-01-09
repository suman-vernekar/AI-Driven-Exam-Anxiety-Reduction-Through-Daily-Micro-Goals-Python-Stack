from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.encouragement import EncouragementResponse, EncouragementCreate
from database.models import EncouragementMessage
from encouragement.engine import encouragement_engine

router = APIRouter()

@router.get("/encouragements/{student_id}", response_model=List[EncouragementResponse])
def get_student_encouragements(student_id: int, db: Session = Depends(get_db)):
    """
    Get all encouragement messages for a specific student
    """
    encouragements = db.query(EncouragementMessage).filter(
        EncouragementMessage.student_id == student_id
    ).order_by(EncouragementMessage.created_at.desc()).all()
    return encouragements

@router.post("/encouragements/generate/{student_id}", response_model=List[EncouragementResponse])
def generate_encouragement_messages(student_id: int, db: Session = Depends(get_db)):
    """
    Generate personalized encouragement messages for a student
    """
    try:
        # Generate encouragement messages using the engine
        encouragement_data = encouragement_engine.generate_personalized_encouragement(db, student_id)
        
        # Save the generated messages to the database
        created_messages = []
        for msg_data in encouragement_data:
            db_message = EncouragementMessage(
                student_id=msg_data.student_id,
                message=msg_data.message,
                message_type=msg_data.message_type
            )
            db.add(db_message)
            db.commit()
            db.refresh(db_message)
            created_messages.append(db_message)
        
        return created_messages
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error generating encouragement messages: {str(e)}")

@router.post("/encouragements/daily/{student_id}", response_model=str)
def get_daily_encouragement(student_id: int, db: Session = Depends(get_db)):
    """
    Get today's daily encouragement message for a student
    """
    try:
        message = encouragement_engine.generate_daily_encouragement(db, student_id)
        
        # Save the message to the database
        db_message = EncouragementMessage(
            student_id=student_id,
            message=message,
            message_type="daily"
        )
        db.add(db_message)
        db.commit()
        
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating daily encouragement: {str(e)}")

@router.put("/encouragements/{message_id}/mark-viewed")
def mark_encouragement_viewed(message_id: int, db: Session = Depends(get_db)):
    """
    Mark an encouragement message as viewed
    """
    message = db.query(EncouragementMessage).filter(
        EncouragementMessage.id == message_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.viewed = True
    db.commit()
    
    return {"message": "Message marked as viewed", "success": True}