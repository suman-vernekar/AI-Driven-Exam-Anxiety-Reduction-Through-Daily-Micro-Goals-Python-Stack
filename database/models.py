from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database setup
DATABASE_URL = "sqlite:///./exam_anxiety.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    grade = Column(String)
    exam_type = Column(String)  # e.g., "board", "competitive"
    created_at = Column(DateTime, default=datetime.utcnow)

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String, index=True)
    syllabus_id = Column(Integer)
    difficulty_level = Column(String)  # "easy", "medium", "hard"
    estimated_time = Column(Integer)  # in minutes

class PerformanceRecord(Base):
    __tablename__ = "performance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    topic_id = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)  # percentage score
    time_spent = Column(Integer)  # in minutes
    mistakes = Column(Text)  # JSON string of mistakes made
    completed = Column(Boolean, default=True)

class MicroGoal(Base):
    __tablename__ = "micro_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    topic_id = Column(Integer)
    goal_text = Column(Text)
    estimated_time = Column(Integer)  # in minutes
    priority = Column(Integer)  # 1-5 priority level
    created_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

class AnxietySignal(Base):
    __tablename__ = "anxiety_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    signal_type = Column(String)  # "stress", "improvement_streak", "consistency", etc.
    value = Column(Float)
    description = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)

class EncouragementMessage(Base):
    __tablename__ = "encouragement_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    message = Column(Text)
    message_type = Column(String)  # "daily", "after_goal", "consolation", etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed = Column(Boolean, default=False)