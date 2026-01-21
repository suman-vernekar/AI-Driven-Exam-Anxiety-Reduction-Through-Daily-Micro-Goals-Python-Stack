from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List

from database.database import engine, Base
from database.models import Student, Topic, PerformanceRecord, MicroGoal, AnxietySignal, EncouragementMessage
from schemas.student import StudentCreate, StudentResponse
from schemas.micro_goal import MicroGoalResponse
from schemas.anxiety_signal import AnxietySignalResponse
from schemas.encouragement import EncouragementResponse
from schemas.progress import ProgressResponse
from api import student_routes, micro_goal_routes, anxiety_signal_routes, encouragement_routes, progress_routes

# Create tables
Base.metadata.create_all(bind=engine) 

# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Exam Anxiety Reduction System",
    description="A system to reduce exam anxiety through daily micro-goals and progress tracking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(student_routes.router, prefix="/api/v1", tags=["students"])
app.include_router(micro_goal_routes.router, prefix="/api/v1", tags=["micro-goals"])
app.include_router(anxiety_signal_routes.router, prefix="/api/v1", tags=["anxiety-signals"])
app.include_router(encouragement_routes.router, prefix="/api/v1", tags=["encouragements"])
app.include_router(progress_routes.router, prefix="/api/v1", tags=["progress"])

@app.get("/")
async def root():
    return {"message": "AI-Driven Exam Anxiety Reduction System"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
