from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.anxiety_signal import AnxietySignalResponse
from database.models import AnxietySignal
from anxiety_signals.engine import anxiety_signals_engine

router = APIRouter()

@router.get("/anxiety-signals/{student_id}", response_model=List[AnxietySignalResponse])
def get_student_anxiety_signals(student_id: int, db: Session = Depends(get_db)):
    """
    Get all anxiety signals for a specific student
    """
    signals = db.query(AnxietySignal).filter(AnxietySignal.student_id == student_id).all()
    return signals

@router.get("/confidence-score/{student_id}", response_model=float)
def get_confidence_score(student_id: int, db: Session = Depends(get_db)):
    """
    Calculate and return the current confidence score for a student
    """
    try:
        confidence_score = anxiety_signals_engine.calculate_confidence_score(db, student_id)
        
        # Save this as an anxiety signal for tracking
        from schemas.anxiety_signal import AnxietySignalCreate
        signal = AnxietySignalCreate(
            student_id=student_id,
            signal_type="confidence",
            value=confidence_score,
            description=f"Current confidence score: {confidence_score}"
        )
        
        db_signal = AnxietySignal(
            student_id=signal.student_id,
            signal_type=signal.signal_type,
            value=signal.value,
            description=signal.description
        )
        db.add(db_signal)
        db.commit()
        
        return confidence_score
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating confidence score: {str(e)}")

@router.post("/detect-anxiety-signals/{student_id}")
def detect_anxiety_signals(student_id: int, db: Session = Depends(get_db)):
    """
    Detect and store anxiety signals based on recent performance
    """
    try:
        signals = anxiety_signals_engine.detect_anxiety_signals(db, student_id)
        
        # Save detected signals to database
        for signal in signals:
            db_signal = AnxietySignal(
                student_id=signal.student_id,
                signal_type=signal.signal_type,
                value=signal.value,
                description=signal.description
            )
            db.add(db_signal)
        
        db.commit()
        
        return {
            "message": f"Detected {len(signals)} anxiety signals",
            "signals": signals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anxiety signals: {str(e)}")