from pydantic import BaseModel
from typing import Dict, List


class WorkoutStatsResponse(BaseModel):
    total_workouts: int
    total_duration_minutes: int
    average_duration_minutes: float
    workouts_by_day: Dict[str, int]


class ExerciseProgressionResponse(BaseModel):
    date: str
    weight: float
    reps: int
    volume: float


class CalendarDataResponse(BaseModel):
    calendar_data: Dict[str, List[Dict]]
