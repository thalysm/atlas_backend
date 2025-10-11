from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
from ...infrastructure.repositories.workout_session_repository import (
    WorkoutSessionRepository,
)


class AnalyticsUseCases:
    def __init__(self, session_repository: WorkoutSessionRepository):
        self.session_repository = session_repository

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
                        if hasattr(set_data, "weight") and hasattr(set_data, "reps"):
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
