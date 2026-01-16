import sqlite3
from datetime import datetime, timedelta
import random
from typing import List, Tuple

# Connect to the database
conn = sqlite3.connect('exam_anxiety.db')
cursor = conn.cursor()

def create_sample_students():
    """Create sample students"""
    students = [
        (1, "Rahul Sharma", "rahul@example.com", "12", "board"), 
        (2, "Priya Patel", "priya@example.com", "12", "competitive"), 
        (3, "Amit Kumar", "amit@example.com", "11", "board"),
        (4, "Sneha Reddy", "sneha@example.com", "12", "competitive"),
        (5, "Vikram Singh", "vikram@example.com", "11", "board")
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO students (id, name, email, grade, exam_type)
        VALUES (?, ?, ?, ?, ?)
    ''', students)
    
    print(f"Created {len(students)} sample students")

def create_sample_topics():
    """Create sample topics for different subjects"""
    topics = [
        (1, "Algebra Basics", "Mathematics", 1, "easy", 20),
        (2, "Quadratic Equations", "Mathematics", 1, "medium", 30),
        (3, "Trigonometry", "Mathematics", 1, "medium", 25),
        (4, "Calculus Intro", "Mathematics", 1, "hard", 35),
        (5, "Coordinate Geometry", "Mathematics", 1, "medium", 30),
        (6, "Atomic Structure", "Chemistry", 2, "easy", 25),
        (7, "Chemical Bonding", "Chemistry", 2, "medium", 30),
        (8, "Organic Chemistry", "Chemistry", 2, "hard", 40),
        (9, "Thermodynamics", "Chemistry", 2, "medium", 35),
        (10, "Periodic Table", "Chemistry", 2, "easy", 20),
        (11, "Motion in One Dimension", "Physics", 3, "easy", 25),
        (12, "Laws of Motion", "Physics", 3, "medium", 30),
        (13, "Work and Energy", "Physics", 3, "medium", 30),
        (14, "Electrostatics", "Physics", 3, "hard", 35),
        (15, "Waves", "Physics", 3, "medium", 25)
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO topics (id, name, subject, syllabus_id, difficulty_level, estimated_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', topics)
    
    print(f"Created {len(topics)} sample topics")

def create_sample_performance_records():
    """Create sample performance records for students"""
    records = []
    
    # Generate performance records for each student
    for student_id in range(1, 6):  # Students 1-5
        for day_offset in range(10):  # Last 10 days
            date = datetime.now() - timedelta(days=day_offset)
            
            for _ in range(random.randint(1, 3)):  # 1-3 records per day
                topic_id = random.randint(1, 15)
                score = random.uniform(40, 95)  # Scores between 40-95%
                time_spent = random.randint(15, 45)  # 15-45 minutes
                
                records.append((
                    student_id, 
                    topic_id, 
                    date.strftime('%Y-%m-%d %H:%M:%S'), 
                    score, 
                    time_spent,
                    None,  # mistakes
                    True   # completed
                ))
    
    cursor.executemany('''
        INSERT INTO performance_records (student_id, topic_id, date, score, time_spent, mistakes, completed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    print(f"Created {len(records)} sample performance records")

def create_sample_micro_goals():
    """Create sample micro goals for students"""
    goals = []
    
    # Generate goals for each student
    for student_id in range(1, 6):
        for i in range(5):  # 5 goals per student
            topic_id = random.randint(1, 15)
            estimated_time = random.randint(15, 40)
            priority = random.randint(1, 5)
            completed = random.choice([True, False])
            
            # Generate goal text based on topic
            topics = ["Algebra", "Trigonometry", "Calculus", "Chemistry", "Physics", "Biology"]
            topic_name = f"Topic {topic_id}"
            
            goal_texts = [
                f"Revise {topic_name} formulas ({estimated_time} mins)",
                f"Practice {random.randint(3, 6)} problems on {topic_name} ({estimated_time} mins)",
                f"Review {topic_name} concepts ({estimated_time} mins)",
                f"Complete {topic_name} exercises ({estimated_time} mins)",
                f"Understand {topic_name} fundamentals ({estimated_time} mins)"
            ]
            
            goal_text = random.choice(goal_texts)
            
            goals.append((
                student_id,
                topic_id,
                goal_text,
                estimated_time,
                priority,
                (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'),
                completed,
                (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S') if completed else None
            ))
    
    cursor.executemany('''
        INSERT INTO micro_goals (student_id, topic_id, goal_text, estimated_time, priority, created_at, completed, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', goals)
    
    print(f"Created {len(goals)} sample micro goals")

def create_sample_anxiety_signals():
    """Create sample anxiety signals"""
    signals = []
    
    for student_id in range(1, 6):
        # Add various types of signals
        signal_types = ["stress", "improvement_streak", "consistency", "confidence"]
        
        for _ in range(3):  # 3 signals per student
            signal_type = random.choice(signal_types)
            value = random.uniform(30, 95)
            
            descriptions = {
                "stress": [
                    "Increased study time with decreasing scores",
                    "Low consistency in study pattern",
                    "Significant performance drop"
                ],
                "improvement_streak": [
                    f"Improvement streak of {random.randint(2, 5)} consecutive sessions",
                    f"Performance increased by {random.randint(5, 15)}%",
                    f"Accuracy improved by {random.randint(5, 12)}%"
                ],
                "consistency": [
                    f"Studied {random.randint(4, 6)} of last 7 days",
                    f"Consistent study pattern for {random.randint(3, 7)} days",
                    f"Regular practice maintained for {random.randint(5, 10)} days"
                ],
                "confidence": [
                    f"Current confidence score: {random.uniform(60, 90):.1f}",
                    f"Confidence level assessment: {random.uniform(65, 95):.1f}",
                    f"Self-assessment confidence: {random.uniform(55, 85):.1f}"
                ]
            }
            
            description = random.choice(descriptions[signal_type])
            
            signals.append((
                student_id,
                signal_type,
                value,
                description,
                (datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%Y-%m-%d %H:%M:%S')
            ))
    
    cursor.executemany('''
        INSERT INTO anxiety_signals (student_id, signal_type, value, description, detected_at)
        VALUES (?, ?, ?, ?, ?)
    ''', signals)
    
    print(f"Created {len(signals)} sample anxiety signals")

def create_sample_encouragements():
    """Create sample encouragement messages"""
    messages = []
    
    encouragement_types = ["daily", "after_goal", "consolation", "improvement"]
    
    for student_id in range(1, 6):
        for msg_type in encouragement_types:
            for _ in range(2):  # 2 messages per type per student
                msg_templates = {
                    "daily": [
                        "Remember, consistency matters more than speed. You're on track!",
                        "Small steps daily lead to big results. Your dedication is noticed!",
                        "Learning takes time. Your patience with the process is a strength.",
                        "Every study session counts, even when progress feels slow.",
                        "Your effort today is building your success tomorrow."
                    ],
                    "after_goal": [
                        "Another goal completed! Your discipline is building your confidence.",
                        "Well done! You're building momentum with completed goals.",
                        "Goal completed! Each small victory counts toward your success.",
                        "Great job finishing that goal! You're making steady progress.",
                        "Completed goal! Every task you finish brings you closer to your target."
                    ],
                    "consolation": [
                        "One missed goal doesn't break your progress. Tomorrow is a new opportunity.",
                        "Setbacks are part of learning. What matters is you keep going.",
                        "Don't let one difficult day discourage you. Your journey continues.",
                        "It's okay to have challenging days. What's important is you're here now.",
                        "Progress isn't always smooth. Your commitment to continue matters."
                    ],
                    "improvement": [
                        f"You improved accuracy by {random.randint(5, 15)}% this week—keep going 💪",
                        "Great progress! Your hard work is showing results.",
                        "Consistency pays off! You've improved by {random.randint(5, 12)}% recently.",
                        "Noticed your improvement! You're on the right track!",
                        "Your dedication is paying off with visible progress!"
                    ]
                }
                
                message = random.choice(msg_templates[msg_type])
                viewed = random.choice([True, False])
                
                messages.append((
                    student_id,
                    message,
                    msg_type,
                    (datetime.now() - timedelta(days=random.randint(0, 4))).strftime('%Y-%m-%d %H:%M:%S'),
                    viewed
                ))
    
    cursor.executemany('''
        INSERT INTO encouragement_messages (student_id, message, message_type, created_at, viewed)
        VALUES (?, ?, ?, ?, ?)
    ''', messages)
    
    print(f"Created {len(messages)} sample encouragement messages")

def main():
    """Main function to create all sample data"""
    print("Creating sample dataset for AI-Driven Exam Anxiety Reduction System...")
    
    # Create all sample data
    create_sample_students()
    create_sample_topics()
    create_sample_performance_records()
    create_sample_micro_goals()
    create_sample_anxiety_signals()
    create_sample_encouragements()
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\nSample dataset created successfully!")
    print("Database file: exam_anxiety.db")
    print("Tables populated with sample data for testing.")

if __name__ == "__main__":
    main()
