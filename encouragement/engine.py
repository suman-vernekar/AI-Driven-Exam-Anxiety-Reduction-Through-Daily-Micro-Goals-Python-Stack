import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict

from database.models import PerformanceRecord, EncouragementMessage, MicroGoal, AnxietySignal
from schemas.encouragement import EncouragementCreate, EncouragementType


class EncouragementEngine:
    def __init__(self):
        # Load spaCy model (simplified - in real implementation, handle model loading properly)
        try:
            self.nlp = None  # Placeholder - would load actual model
        except:
            self.nlp = None  # Fallback if model not available
            
        # Positive encouragement templates
        self.positive_templates = {
            "improvement": [
                "You improved accuracy by {improvement}% this week—keep going 💪",
                "Great progress! Your hard work is showing results with {improvement}% improvement.",
                "Consistency pays off! You've improved by {improvement}% recently.",
                "Noticed your improvement of {improvement}% - you're on the right track!",
                "Your dedication is paying off with {improvement}% progress!"
            ],
            "consistency": [
                "Consistency matters more than speed. You're on track with {days} days in a row!",
                "You've been studying for {days} consecutive days - that's commitment!",
                "Daily practice is building your confidence. Keep up the {days} day streak!",
                "Your consistency is impressive - {days} days of focused study!",
                "Small steps daily lead to big results. {days} days of consistency shows your dedication!"
            ],
            "goal_completion": [
                "Another goal completed! Your discipline is building your confidence.",
                "Well done! You're building momentum with completed goals.",
                "Goal completed! Each small victory counts toward your success.",
                "Great job finishing that goal! You're making steady progress.",
                "Completed goal! Every task you finish brings you closer to your target."
            ],
            "effort_recognition": [
                "It's not about speed, it's about persistence. Your effort matters.",
                "Progress isn't always linear. Your consistent effort is building confidence.",
                "Every study session counts, even when progress feels slow.",
                "Your dedication to showing up matters more than perfection.",
                "Learning takes time. Your patience with the process is a strength."
            ]
        }
        
        # Supportive templates for challenging times
        self.supportive_templates = {
            "setback": [
                "One missed goal doesn't break your progress. Tomorrow is a new opportunity.",
                "Setbacks are part of learning. What matters is you keep going.",
                "Don't let one difficult day discourage you. Your journey continues.",
                "It's okay to have challenging days. What's important is you're here now.",
                "Progress isn't always smooth. Your commitment to continue matters."
            ],
            "stress": [
                "Remember: consistency over intensity. You're doing better than you think.",
                "Take breaks when needed. Quality over quantity in your preparation.",
                "Your worth isn't defined by test scores. Focus on your growth journey.",
                "Learning is a marathon, not a sprint. Pace yourself appropriately.",
                "It's normal to feel challenged. Trust in your preparation and growth."
            ]
        }

    def generate_daily_encouragement(self, db: Session, student_id: int) -> str:
        """
        Generate personalized daily encouragement message based on recent activity
        """
        # Analyze recent performance and behavior
        analysis = self._analyze_student_progress(db, student_id)
        
        # Select appropriate template based on analysis
        if analysis.get('significant_improvement', 0) > 5:  # More than 5% improvement
            template = random.choice(self.positive_templates["improvement"])
            return template.format(improvement=round(analysis['significant_improvement'], 1))
        elif analysis.get('consistency_days', 0) >= 3:
            template = random.choice(self.positive_templates["consistency"])
            return template.format(days=analysis['consistency_days'])
        elif analysis.get('recent_goal_completion', False):
            template = random.choice(self.positive_templates["goal_completion"])
            return template
        elif analysis.get('stress_signals', 0) > 0:
            template = random.choice(self.supportive_templates["stress"])
            return template
        else:
            # Default encouraging message
            return "Remember, every expert was once a beginner. Your consistent effort is building your success!"

    def generate_after_goal_encouragement(self, db: Session, student_id: int, goal_id: int) -> str:
        """
        Generate encouragement after completing a micro goal
        """
        # Get goal details
        goal = db.query(MicroGoal).filter(MicroGoal.id == goal_id).first()
        if not goal:
            return "Goal completed! Keep up the good work!"
        
        # Generate specific encouragement based on goal type
        if "revise" in goal.goal_text.lower() or "review" in goal.goal_text.lower():
            return "Great job reviewing concepts! Repetition strengthens memory and builds confidence."
        elif "practice" in goal.goal_text.lower() or "solve" in goal.goal_text.lower():
            return "Practice makes progress! Each problem you solve builds your confidence for the exam."
        else:
            return "Goal completed! Each small step brings you closer to your success."

    def generate_improvement_encouragement(self, db: Session, student_id: int, improvement_percentage: float) -> str:
        """
        Generate encouragement when improvement is detected
        """
        template = random.choice(self.positive_templates["improvement"])
        return template.format(improvement=round(improvement_percentage, 1))

    def generate_setback_encouragement(self, db: Session, student_id: int) -> str:
        """
        Generate supportive message during difficult periods
        """
        # Check if there are recent stress signals
        stress_signals = db.query(AnxietySignal).filter(
            AnxietySignal.student_id == student_id,
            AnxietySignal.signal_type == "stress",
            AnxietySignal.detected_at >= datetime.utcnow() - timedelta(days=2)
        ).count()
        
        if stress_signals > 0:
            template = random.choice(self.supportive_templates["stress"])
        else:
            template = random.choice(self.supportive_templates["setback"])
        
        return template

    def _analyze_student_progress(self, db: Session, student_id: int) -> Dict:
        """
        Analyze student's recent progress to inform encouragement
        """
        analysis = {}
        
        # Get recent performance (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_performance = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id,
            PerformanceRecord.date >= seven_days_ago
        ).order_by(PerformanceRecord.date).all()
        
        # Calculate improvement
        if len(recent_performance) >= 2:
            first_score = recent_performance[0].score
            last_score = recent_performance[-1].score
            improvement = ((last_score - first_score) / first_score * 100) if first_score != 0 else 0
            analysis['significant_improvement'] = improvement
        else:
            analysis['significant_improvement'] = 0
        
        # Check consistency (days active in last 7 days)
        study_dates = set()
        for record in recent_performance:
            study_dates.add(record.date.date())
        analysis['consistency_days'] = len(study_dates)
        
        # Check recent goal completion
        recent_goals = db.query(MicroGoal).filter(
            MicroGoal.student_id == student_id,
            MicroGoal.completed == True,
            MicroGoal.completed_at >= seven_days_ago
        ).count()
        analysis['recent_goal_completion'] = recent_goals > 0
        
        # Check for stress signals
        stress_signals = db.query(AnxietySignal).filter(
            AnxietySignal.student_id == student_id,
            AnxietySignal.signal_type == "stress",
            AnxietySignal.detected_at >= seven_days_ago
        ).count()
        analysis['stress_signals'] = stress_signals
        
        return analysis

    def generate_personalized_encouragement(self, db: Session, student_id: int) -> List[EncouragementCreate]:
        """
        Generate multiple types of personalized encouragement messages
        """
        encouragements = []
        
        # Daily encouragement
        daily_msg = self.generate_daily_encouragement(db, student_id)
        encouragements.append(EncouragementCreate(
            student_id=student_id,
            message=daily_msg,
            message_type=EncouragementType.daily
        ))
        
        # Additional messages based on analysis
        analysis = self._analyze_student_progress(db, student_id)
        
        if analysis.get('significant_improvement', 0) > 10:  # Significant improvement
            improvement_msg = self.generate_improvement_encouragement(
                db, student_id, analysis['significant_improvement']
            )
            encouragements.append(EncouragementCreate(
                student_id=student_id,
                message=improvement_msg,
                message_type=EncouragementType.improvement
            ))
        elif analysis.get('stress_signals', 0) > 0:  # If there are stress signals
            setback_msg = self.generate_setback_encouragement(db, student_id)
            encouragements.append(EncouragementCreate(
                student_id=student_id,
                message=setback_msg,
                message_type=EncouragementType.consolation
            ))
        
        return encouragements


# Initialize the encouragement engine
encouragement_engine = EncouragementEngine()