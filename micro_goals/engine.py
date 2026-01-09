import random
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from sqlalchemy.orm import Session

from database.models import PerformanceRecord, Topic, MicroGoal
from schemas.micro_goal import MicroGoalCreate


class MicroGoalEngine:
    def __init__(self):
        self.time_box_options = {
            "short": (10, 20),      # 10-20 minutes
            "medium": (20, 35),     # 20-35 minutes
            "long": (35, 50)        # 35-50 minutes
        }
        
        self.goal_templates = {
            "revision": [
                "Revise {topic_name} formulas/concepts ({time_estimate} mins)",
                "Review {topic_name} key points ({time_estimate} mins)",
                "Go through {topic_name} notes ({time_estimate} mins)"
            ],
            "practice": [
                "Attempt {num_questions} {difficulty} questions from {topic_name} ({time_estimate} mins)",
                "Solve {num_questions} {difficulty} problems on {topic_name} ({time_estimate} mins)",
                "Practice {topic_name} with {num_questions} questions - no time pressure ({time_estimate} mins)"
            ],
            "conceptual": [
                "Understand core concepts of {topic_name} ({time_estimate} mins)",
                "Focus on {topic_name} fundamentals ({time_estimate} mins)",
                "Clear {topic_name} doubts ({time_estimate} mins)"
            ]
        }

    def generate_daily_goals(self, db: Session, student_id: int) -> List[MicroGoalCreate]:
        """
        Generate 2-4 small, realistic daily goals based on:
        - Student's syllabus (topics)
        - Performance history
        - Current preparation level
        """
        # Get all topics for the student's syllabus
        topics = db.query(Topic).all()
        
        # Get recent performance records
        recent_date = datetime.utcnow() - timedelta(days=7)  # Last 7 days
        recent_performance = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id,
            PerformanceRecord.date >= recent_date
        ).all()
        
        # Analyze performance data
        performance_df = self._create_performance_dataframe(recent_performance)
        
        # Generate goals based on performance analysis
        goals = []
        
        # Identify weak areas (low scores or high mistakes)
        weak_topics = self._identify_weak_topics(performance_df)
        
        # Identify topics not practiced recently
        inactive_topics = self._identify_inactive_topics(topics, recent_performance)
        
        # Generate goals based on analysis
        goals.extend(self._generate_goals_for_weak_topics(weak_topics, 2))  # 2 goals for weak areas
        goals.extend(self._generate_goals_for_inactive_topics(inactive_topics, 1))  # 1 goal for inactive topics
        
        # Add one confidence-building goal
        goals.append(self._generate_confidence_goal(topics))
        
        # Ensure we have 2-4 goals
        while len(goals) < 2:
            goals.append(self._generate_additional_goal(topics))
        
        # Limit to 4 goals maximum
        goals = goals[:4]
        
        # Convert to MicroGoalCreate objects
        micro_goals = []
        for goal in goals:
            micro_goal = MicroGoalCreate(
                student_id=student_id,
                topic_id=goal['topic_id'],
                goal_text=goal['text'],
                estimated_time=goal['time'],
                priority=goal['priority']
            )
            micro_goals.append(micro_goal)
        
        return micro_goals

    def _create_performance_dataframe(self, performance_records: List[PerformanceRecord]) -> pd.DataFrame:
        """Convert performance records to pandas DataFrame for analysis"""
        if not performance_records:
            return pd.DataFrame(columns=['topic_id', 'score', 'time_spent', 'date'])
        
        data = []
        for record in performance_records:
            data.append({
                'topic_id': record.topic_id,
                'score': record.score,
                'time_spent': record.time_spent,
                'date': record.date
            })
        
        return pd.DataFrame(data)

    def _identify_weak_topics(self, performance_df: pd.DataFrame) -> List[Dict]:
        """Identify topics where student is performing poorly"""
        if performance_df.empty:
            return []
        
        # Group by topic and calculate average performance
        topic_performance = performance_df.groupby('topic_id').agg({
            'score': ['mean', 'count'],
            'time_spent': 'mean'
        }).round(2)
        
        # Flatten column names
        topic_performance.columns = ['_'.join(col).strip() for col in topic_performance.columns]
        
        # Identify topics with low average scores (less than 70%)
        weak_topics = topic_performance[topic_performance['score_mean'] < 70.0]
        
        result = []
        for topic_id, row in weak_topics.iterrows():
            result.append({
                'topic_id': int(topic_id),
                'avg_score': float(row['score_mean']),
                'attempts': int(row['score_count']),
                'avg_time_spent': float(row['time_spent_mean'])
            })
        
        return result

    def _identify_inactive_topics(self, all_topics: List[Topic], recent_performance: List[PerformanceRecord]) -> List[Topic]:
        """Identify topics that haven't been practiced recently"""
        active_topic_ids = set(record.topic_id for record in recent_performance)
        inactive_topics = [topic for topic in all_topics if topic.id not in active_topic_ids]
        return inactive_topics

    def _generate_goals_for_weak_topics(self, weak_topics: List[Dict], count: int) -> List[Dict]:
        """Generate goals targeting weak topics"""
        goals = []
        
        for i, weak_topic in enumerate(weak_topics[:count]):
            # Select a template based on the weakness
            if weak_topic['avg_score'] < 50:
                # Very weak topic - focus on revision
                template = random.choice(self.goal_templates["revision"])
                time_range = self.time_box_options["medium"]
            else:
                # Moderately weak - mix of revision and practice
                template = random.choice(self.goal_templates["practice"])
                time_range = self.time_box_options["short"]
            
            time_estimate = random.randint(time_range[0], time_range[1])
            topic_name = f"Topic {weak_topic['topic_id']}"  # In real implementation, get actual topic name
            
            goal_text = template.format(
                topic_name=topic_name,
                time_estimate=time_estimate,
                num_questions=random.randint(3, 6),
                difficulty="easy"
            )
            
            goals.append({
                'topic_id': weak_topic['topic_id'],
                'text': goal_text,
                'time': time_estimate,
                'priority': 5  # High priority for weak areas
            })
        
        # If we don't have enough weak topics, add additional goals
        while len(goals) < count:
            goals.append(self._generate_additional_goal([]))
        
        return goals

    def _generate_goals_for_inactive_topics(self, inactive_topics: List[Topic], count: int) -> List[Dict]:
        """Generate goals for topics that haven't been practiced recently"""
        goals = []
        
        for i in range(min(count, len(inactive_topics))):
            topic = inactive_topics[i]
            template = random.choice(self.goal_templates["revision"])
            time_range = self.time_box_options["short"]
            time_estimate = random.randint(time_range[0], time_range[1])
            
            goal_text = template.format(
                topic_name=topic.name,
                time_estimate=time_estimate
            )
            
            goals.append({
                'topic_id': topic.id,
                'text': goal_text,
                'time': time_estimate,
                'priority': 3  # Medium priority
            })
        
        # If no inactive topics, generate additional goals
        while len(goals) < count:
            goals.append(self._generate_additional_goal(inactive_topics))
        
        return goals

    def _generate_confidence_goal(self, all_topics: List[Topic]) -> Dict:
        """Generate a confidence-building goal based on a well-performing topic"""
        # For now, pick a random topic
        if all_topics:
            topic = random.choice(all_topics)
        else:
            topic = type('obj', (object,), {'id': 1, 'name': 'General Topic'})()
        
        template = random.choice(self.goal_templates["conceptual"])
        time_range = self.time_box_options["short"]
        time_estimate = random.randint(time_range[0], time_range[1])
        
        goal_text = template.format(
            topic_name=topic.name,
            time_estimate=time_estimate
        )
        
        return {
            'topic_id': topic.id,
            'text': goal_text,
            'time': time_estimate,
            'priority': 2  # Lower priority for confidence building
        }

    def _generate_additional_goal(self, all_topics: List[Topic]) -> Dict:
        """Generate an additional goal when we don't have enough targets"""
        if all_topics:
            topic = random.choice(all_topics)
        else:
            topic = type('obj', (object,), {'id': 1, 'name': 'General Topic'})()
        
        templates = self.goal_templates["revision"] + self.goal_templates["practice"]
        template = random.choice(templates)
        time_range = self.time_box_options["short"]
        time_estimate = random.randint(time_range[0], time_range[1])
        
        goal_text = template.format(
            topic_name=topic.name,
            time_estimate=time_estimate,
            num_questions=random.randint(3, 5),
            difficulty="easy"
        )
        
        return {
            'topic_id': topic.id,
            'text': goal_text,
            'time': time_estimate,
            'priority': 3  # Medium priority
        }


# Initialize the micro-goal engine
micro_goal_engine = MicroGoalEngine()