import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from sklearn.linear_model import LinearRegression

from database.models import PerformanceRecord, AnxietySignal, MicroGoal
from schemas.anxiety_signal import AnxietySignalCreate


class AnxietySignalsEngine:
    def __init__(self):
        self.confidence_weight_factors = {
            'consistency': 0.25,           # Consistency of study days
            'improvement_streak': 0.25,    # Streaks of improvement
            'mistake_reduction': 0.20,     # Reduction in repeated mistakes
            'goal_completion_rate': 0.15,  # Rate of completing daily goals
            'performance_trend': 0.15      # Overall performance trend
        }

    def calculate_confidence_score(self, db: Session, student_id: int) -> float:
        """
        Calculate a confidence score (0-100) based on multiple factors
        """
        # Get recent performance data (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        performance_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id,
            PerformanceRecord.date >= thirty_days_ago
        ).order_by(PerformanceRecord.date).all()
        
        if not performance_records:
            return 50.0  # Neutral score if no data
        
        # Calculate individual factors
        consistency_score = self._calculate_consistency_score(db, student_id)
        improvement_streak_score = self._calculate_improvement_streak_score(performance_records)
        mistake_reduction_score = self._calculate_mistake_reduction_score(performance_records)
        goal_completion_score = self._calculate_goal_completion_score(db, student_id)
        performance_trend_score = self._calculate_performance_trend_score(performance_records)
        
        # Weighted combination of factors
        confidence_score = (
            consistency_score * self.confidence_weight_factors['consistency'] +
            improvement_streak_score * self.confidence_weight_factors['improvement_streak'] +
            mistake_reduction_score * self.confidence_weight_factors['mistake_reduction'] +
            goal_completion_score * self.confidence_weight_factors['goal_completion_rate'] +
            performance_trend_score * self.confidence_weight_factors['performance_trend']
        )
        
        # Ensure score is between 0 and 100
        confidence_score = max(0, min(100, confidence_score))
        
        return round(confidence_score, 2)

    def detect_anxiety_signals(self, db: Session, student_id: int) -> List[AnxietySignalCreate]:
        """
        Detect various anxiety signals based on performance and behavior patterns
        """
        signals = []
        
        # Get recent data
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        performance_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id,
            PerformanceRecord.date >= thirty_days_ago
        ).order_by(PerformanceRecord.date).all()
        
        # Detect stress indicators
        stress_signals = self._detect_stress_signals(performance_records, student_id)
        signals.extend(stress_signals)
        
        # Detect improvement streaks
        improvement_signals = self._detect_improvement_signals(performance_records, student_id)
        signals.extend(improvement_signals)
        
        # Detect consistency patterns
        consistency_signals = self._detect_consistency_signals(db, student_id)
        signals.extend(consistency_signals)
        
        return signals

    def _calculate_consistency_score(self, db: Session, student_id: int) -> float:
        """
        Calculate consistency score based on study day frequency
        """
        # Get dates of activity in the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        performance_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id,
            PerformanceRecord.date >= thirty_days_ago
        ).all()
        
        # Get unique study days
        study_dates = set()
        for record in performance_records:
            study_dates.add(record.date.date())
        
        # Calculate consistency as percentage of days studied
        total_days = 30
        active_days = len(study_dates)
        consistency_percentage = (active_days / total_days) * 100
        
        # Cap at 100
        consistency_score = min(100, consistency_percentage * 3)  # Amplify slightly since 30 days is a lot
        return min(100, consistency_score)

    def _calculate_improvement_streak_score(self, performance_records: List[PerformanceRecord]) -> float:
        """
        Calculate improvement streak score based on consecutive improvement
        """
        if len(performance_records) < 2:
            return 50.0  # Neutral score
        
        # Calculate improvement streak
        improvements = 0
        total_comparisons = 0
        
        for i in range(1, len(performance_records)):
            prev_score = performance_records[i-1].score
            curr_score = performance_records[i].score
            
            if curr_score > prev_score:
                improvements += 1
            total_comparisons += 1
        
        if total_comparisons == 0:
            return 50.0
        
        improvement_rate = (improvements / total_comparisons) * 100
        return min(100, improvement_rate)

    def _calculate_mistake_reduction_score(self, performance_records: List[PerformanceRecord]) -> float:
        """
        Calculate score based on reduction in repeated mistakes
        """
        if len(performance_records) < 2:
            return 50.0  # Neutral score
        
        # Simplified calculation - in real implementation, parse mistake data properly
        # For now, we'll use score improvement as a proxy for mistake reduction
        first_score = performance_records[0].score
        last_score = performance_records[-1].score
        
        if first_score == 0:
            if last_score > 0:
                return 100.0
            else:
                return 50.0
        
        # Calculate improvement percentage
        improvement = ((last_score - first_score) / first_score) * 100
        # Normalize to 0-100 scale
        mistake_reduction_score = 50 + (improvement * 0.5)  # Adjust scaling factor
        
        return max(0, min(100, mistake_reduction_score))

    def _calculate_goal_completion_score(self, db: Session, student_id: int) -> float:
        """
        Calculate score based on goal completion rate
        """
        # Get recent goals (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        goals = db.query(MicroGoal).filter(
            MicroGoal.student_id == student_id,
            MicroGoal.created_at >= thirty_days_ago
        ).all()
        
        if not goals:
            return 50.0  # Neutral score
        
        completed_goals = sum(1 for goal in goals if goal.completed)
        completion_rate = (completed_goals / len(goals)) * 100
        
        return completion_rate

    def _calculate_performance_trend_score(self, performance_records: List[PerformanceRecord]) -> float:
        """
        Calculate score based on overall performance trend using linear regression
        """
        if len(performance_records) < 2:
            return 50.0  # Neutral score
        
        # Prepare data for regression
        dates = []
        scores = []
        
        for record in performance_records:
            # Convert date to ordinal for regression
            dates.append(record.date.toordinal())
            scores.append(record.score)
        
        # Perform linear regression
        X = np.array(dates).reshape(-1, 1)
        y = np.array(scores)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Get slope of the trend line
        slope = model.coef_[0]
        
        # Calculate trend strength score (0-100)
        # A perfectly flat line would be neutral (50), positive slope increases score, negative decreases
        base_score = 50.0
        trend_strength = slope * 10  # Adjust multiplier as needed
        trend_score = base_score + trend_strength
        
        return max(0, min(100, trend_score))

    def _detect_stress_signals(self, performance_records: List[PerformanceRecord], student_id: int) -> List[AnxietySignalCreate]:
        """
        Detect stress-related signals from performance data
        """
        signals = []
        
        if len(performance_records) < 3:
            return signals
        
        # Detect sudden drops in performance
        for i in range(2, len(performance_records)):
            prev_avg = (performance_records[i-2].score + performance_records[i-1].score) / 2
            current = performance_records[i].score
            
            if current < prev_avg * 0.7:  # More than 30% drop
                signals.append(AnxietySignalCreate(
                    student_id=student_id,
                    signal_type="stress",
                    value=75.0,
                    description=f"Sudden performance drop detected: {prev_avg:.1f}% -> {current:.1f}%"
                ))
        
        # Detect increased time spent with decreasing scores (possible stress indicator)
        for i in range(1, len(performance_records)):
            time_diff = performance_records[i].time_spent - performance_records[i-1].time_spent
            score_diff = performance_records[i].score - performance_records[i-1].score
            
            if time_diff > 10 and score_diff < 0:  # Spent 10+ more mins but scored lower
                signals.append(AnxietySignalCreate(
                    student_id=student_id,
                    signal_type="stress",
                    value=60.0,
                    description=f"Increased study time with decreased performance: spent {performance_records[i].time_spent} vs {performance_records[i-1].time_spent} mins"
                ))
        
        return signals

    def _detect_improvement_signals(self, performance_records: List[PerformanceRecord], student_id: int) -> List[AnxietySignalCreate]:
        """
        Detect positive improvement signals
        """
        signals = []
        
        if len(performance_records) < 2:
            return signals
        
        # Count improvement streaks
        streak = 0
        max_streak = 0
        
        for i in range(1, len(performance_records)):
            if performance_records[i].score > performance_records[i-1].score:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        
        if max_streak >= 3:  # At least 3 consecutive improvements
            signals.append(AnxietySignalCreate(
                student_id=student_id,
                signal_type="improvement_streak",
                value=max_streak,
                description=f"Improvement streak of {max_streak} consecutive sessions"
            ))
        
        return signals

    def _detect_consistency_signals(self, db: Session, student_id: int) -> List[AnxietySignalCreate]:
        """
        Detect consistency-related signals
        """
        signals = []
        
        # Calculate consistency (days active in last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id,
            PerformanceRecord.date >= seven_days_ago
        ).all()
        
        # Count unique study days
        study_dates = set(record.date.date() for record in recent_records)
        consistency_days = len(study_dates)
        
        if consistency_days >= 5:  # 5+ days in last week
            signals.append(AnxietySignalCreate(
                student_id=student_id,
                signal_type="consistency",
                value=consistency_days,
                description=f"High consistency: studied {consistency_days} of last 7 days"
            ))
        elif consistency_days <= 2:  # 2 or fewer days in last week
            signals.append(AnxietySignalCreate(
                student_id=student_id,
                signal_type="stress",
                value=40.0,
                description=f"Low consistency: studied only {consistency_days} of last 7 days"
            ))
        
        return signals


# Initialize the anxiety signals engine
anxiety_signals_engine = AnxietySignalsEngine()