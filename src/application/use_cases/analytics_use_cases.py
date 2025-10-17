from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from ...infrastructure.repositories.workout_session_repository import (
    WorkoutSessionRepository,
)
from ...infrastructure.repositories.water_intake_repository import WaterIntakeRepository
from ...infrastructure.repositories.user_repository import UserRepository
from ...domain.entities.workout_session import StrengthSet


class AnalyticsUseCases:
    def __init__(self, session_repository: WorkoutSessionRepository, water_intake_repository: WaterIntakeRepository, user_repository: UserRepository):
        self.session_repository = session_repository
        self.water_intake_repository = water_intake_repository
        self.user_repository = user_repository

    async def get_workout_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get workout statistics for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        sessions = await self.session_repository.find_by_user_and_date_range(
            user_id, start_date, end_date
        )

        completed_sessions = [s for s in sessions if s.is_completed]

        # Calculate stats
        total_workouts = len(completed_sessions)
        total_duration = sum(s.duration_minutes or 0 for s in completed_sessions)
        avg_duration = total_duration / total_workouts if total_workouts > 0 else 0
        
        # New Stats
        total_volume = 0
        exercise_counts = Counter()

        for session in completed_sessions:
            for exercise_log in session.exercises:
                exercise_counts[exercise_log.exercise_name] += 1
                if exercise_log.type == "strength":
                    for s_set in exercise_log.sets:
                        if isinstance(s_set, StrengthSet):
                            total_volume += s_set.weight * s_set.reps
        
        most_frequent_exercise = exercise_counts.most_common(1)
        most_frequent_exercise_data = {
            "name": most_frequent_exercise[0][0],
            "count": most_frequent_exercise[0][1]
        } if most_frequent_exercise else None

        # Workouts by day
        workouts_by_day = defaultdict(int)
        for session in completed_sessions:
            day = session.start_time.date().isoformat()
            workouts_by_day[day] += 1

        return {
            "total_workouts": total_workouts,
            "total_duration_minutes": total_duration,
            "average_duration_minutes": round(avg_duration, 1),
            "workouts_by_day": dict(workouts_by_day),
            "total_volume": round(total_volume),
            "weekly_frequency": round((total_workouts / days) * 7, 1) if days > 0 else 0,
            "most_frequent_exercise": most_frequent_exercise_data,
        }

    async def get_exercise_progression(
        self, user_id: str, exercise_id: str, days: int = 90
    ) -> List[Dict]:
        """Get progression data for a specific exercise"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        sessions = await self.session_repository.find_by_user_and_date_range(
            user_id, start_date, end_date
        )

        progression_data = []

        for session in sessions:
            if not session.is_completed:
                continue

            for exercise_log in session.exercises:
                if exercise_log.exercise_id == exercise_id:
                    for set_data in exercise_log.sets:
                        if isinstance(set_data, StrengthSet):
                            progression_data.append(
                                {
                                    "date": session.start_time.isoformat(),
                                    "weight": set_data.weight,
                                    "reps": set_data.reps,
                                    "volume": set_data.weight * set_data.reps,
                                }
                            )

        return progression_data

    async def get_calendar_data(
        self, user_id: str, year: int, month: int
    ) -> Dict[str, List[Dict]]:
        """Get workout sessions grouped by date for calendar view"""
        # Get first and last day of the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        end_date = end_date.replace(hour=23, minute=59, second=59)


        sessions = await self.session_repository.find_by_user_and_date_range(
            user_id, start_date, end_date
        )

        # Group by date
        calendar_data = defaultdict(list)
        for session in sessions:
            if session.is_completed:
                day = session.start_time.date().isoformat()
                calendar_data[day].append(
                    {
                        "id": str(session.id),
                        "package_name": session.package_name,
                        "duration_minutes": session.duration_minutes,
                        "start_time": session.start_time.isoformat(),
                    }
                )

        return dict(calendar_data)

    async def get_water_consumption_stats(self, user_id: str, days: int) -> Dict:
        """Get daily water consumption for the last N days"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        intakes = await self.water_intake_repository.find_by_user_and_date_range(user_id, start_date, end_date)
        
        consumption_by_day = defaultdict(int)
        for intake in intakes:
            day = intake.created_at.date().isoformat()
            consumption_by_day[day] += intake.amount_ml
            
        return dict(consumption_by_day)

    async def calculate_daily_water_recommendation(self, user_id: str) -> Dict:
        """Calculate daily water recommendation based on user's weight"""
        user = await self.user_repository.find_by_id(user_id)
        if not user or not user.weight or user.weight <= 0:
            # Default recommendation if no weight is available
            return {"recommendation_ml": 2000}
        
        # 35ml per kg of body weight
        recommendation = user.weight * 35
        return {"recommendation_ml": round(recommendation)}