from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.database import get_db
from schemas.student import StudentCreate, StudentResponse
from schemas.performance import PerformanceRecordCreate, PerformanceRecordResponse
from database.models import Student, PerformanceRecord

router = APIRouter()

@router.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student
    """
    try:
        # Check if student with this email already exists
        existing_student = db.query(Student).filter(Student.email == student.email).first()
        if existing_student:
            raise HTTPException(status_code=400, detail="Student with this email already exists")
        
        # Create new student
        db_student = Student(
            name=student.name,
            email=student.email,
            grade=student.grade,
            exam_type=student.exam_type
        )
        
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        
        return db_student
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating student: {str(e)}")

@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Get a student by ID
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.get("/students", response_model=List[StudentResponse])
def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all students
    """
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.post("/performance-records", response_model=PerformanceRecordResponse)
def create_performance_record(
    performance_record: PerformanceRecordCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new performance record
    """
    try:
        db_record = PerformanceRecord(
            student_id=performance_record.student_id,
            topic_id=performance_record.topic_id,
            score=performance_record.score,
            time_spent=performance_record.time_spent,
            mistakes=performance_record.mistakes,
            completed=performance_record.completed
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return db_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating performance record: {str(e)}")

@router.get("/performance-records/{student_id}", response_model=List[PerformanceRecordResponse])
def get_student_performance_records(
    student_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Get all performance records for a specific student
    """
    records = db.query(PerformanceRecord).filter(
        PerformanceRecord.student_id == student_id
    ).order_by(PerformanceRecord.date.desc()).offset(skip).limit(limit).all()
    
    return records