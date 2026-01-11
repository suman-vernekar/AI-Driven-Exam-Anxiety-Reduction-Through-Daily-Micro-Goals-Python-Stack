# AI-Driven Exam Anxiety Reduction Through Daily Micro-Goals

## Project Overview
This system uses artificial intelligence to help students reduce exam anxiety by converting their syllabus and performance data into small, achievable daily micro-goals. The system tracks progress, generates personalized encouragement, and provides an exam readiness score to help students stay motivated and confident.

## Features

### 1. Daily Micro-Goal Engine
- Generates 2-4 personalized daily goals based on student performance
- Time-boxed goals (typically 10-50 minutes)
- Low cognitive load to reduce stress
- Goals are clearly completable in one sitting

### 2. Progress Tracking & Anxiety Signals
- Confidence scoring algorithm with weighted factors
- Tracks consistency, improvement streaks, and mistake reduction
- Detects anxiety indicators and stress patterns
- Provides exam readiness score (0-100 scale) 

### 3. Encouragement & Feedback Engine
- Empathetic, data-driven motivational messages
- Non-judgmental feedback based on real progress
- Templates that adapt to individual student needs
- Clear explanations of why each message is shown

### 4. Minimal Dashboard
- Clean, student-first user interface
- Displays today's micro-goals
- Progress streak visualization
- Confidence trend tracking
- Positive reinforcement messages
- No peer comparisons or rankings

## Tech Stack
- **Backend**: FastAPI with Pydantic models
- **Database**: SQLite with SQLAlchemy ORM
- **Analytics**: Pandas, NumPy, scikit-learn
- **NLP**: spaCy-ready templates for encouragement
- **Frontend**: Streamlit dashboard
- **APIs**: Clean REST endpoints

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create the database:
   ```
   python populate_sample_data.py
   ```
4. Start the backend:
   ```
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5. Start the dashboard:
   ```
   python -m streamlit run dashboard/app.py
   ```

## Usage

1. Access the dashboard at `http://localhost:8501`
2. Enter your student ID in the sidebar
3. Navigate to the "Daily Goals" tab to see your micro-goals
4. Log performance data in the "Log Performance Data" section
5. View progress in the "Progress & Confidence Tracking" tab
6. Get encouragement from the "Encouragement Messages" tab
7. Analyze trends in the "Analytics Dashboard" tab

## Key Algorithms

### Confidence Scoring
- Consistency (25%): Regular study patterns
- Improvement Streaks (25%): Continuous progress
- Mistake Reduction (20%): Fewer repeated errors
- Goal Completion Rate (15%): Achieving set targets
- Performance Trend (15%): Overall academic trajectory

### Micro-Goal Generation
- Analyzes weak and inactive topics
- Considers time availability and performance history
- Balances difficulty and achievability
- Provides specific, actionable goals

## Data Privacy
- All data stored locally in SQLite database
- No personal information shared externally
- Students control their own data

## Architecture
```
exam_anxiety_reduction/
├── api/                    # REST API endpoints
├── models/                 # Database models
├── schemas/               # Pydantic models
├── database/              # Database configuration
├── micro_goals/           # Goal generation engine
├── anxiety_signals/       # Confidence scoring
├── encouragement/         # Feedback engine
├── dashboard/             # Streamlit UI
├── main.py               # Application entry point
├── populate_sample_data.py # Sample data generator
└── requirements.txt       # Dependencies
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT License

## Acknowledgments
- Developed as part of a hackathon project focused on student mental health
- Inspired by research on micro-goal achievement and anxiety reduction
- Built with educational psychology principles in mind
