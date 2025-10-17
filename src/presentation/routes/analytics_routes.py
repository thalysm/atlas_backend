from fastapi import APIRouter, Depends, Query
from typing import List, Dict
from ..schemas.analytics_schemas import (
    WorkoutStatsResponse,
    ExerciseProgressionResponse,
    CalendarDataResponse,
)
from ..dependencies import get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.workout_session_repository import (
    WorkoutSessionRepository,
)
from ...infrastructure.repositories.water_intake_repository import WaterIntakeRepository
from ...infrastructure.repositories.user_repository import UserRepository
from ...application.use_cases.analytics_use_cases import AnalyticsUseCases

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_use_cases() -> AnalyticsUseCases:
    db = get_database()
    session_repository = WorkoutSessionRepository(db)
    water_repo = WaterIntakeRepository(db)
    user_repo = UserRepository(db)
    return AnalyticsUseCases(session_repository, water_repo, user_repo)


@router.get("/stats", response_model=WorkoutStatsResponse)
async def get_workout_stats(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    analytics_use_cases: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    """Get workout statistics"""
    stats = await analytics_use_cases.get_workout_stats(user_id, days)
    return stats


@router.get("/progression/{exercise_id}", response_model=List[ExerciseProgressionResponse])
async def get_exercise_progression(
    exercise_id: str,
    days: int = Query(90, ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    analytics_use_cases: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    """Get exercise progression data"""
    progression = await analytics_use_cases.get_exercise_progression(
        user_id, exercise_id, days
    )
    return progression


@router.get("/calendar", response_model=CalendarDataResponse)
async def get_calendar_data(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    user_id: str = Depends(get_current_user_id),
    analytics_use_cases: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    """Get calendar data for a specific month"""
    calendar_data = await analytics_use_cases.get_calendar_data(user_id, year, month)
    return {"calendar_data": calendar_data}


@router.get("/water/recommendation", response_model=Dict)
async def get_water_recommendation(
    user_id: str = Depends(get_current_user_id),
    analytics_use_cases: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    """Calculate daily water recommendation"""
    recommendation = await analytics_use_cases.calculate_daily_water_recommendation(user_id)
    return recommendation

@router.get("/water/stats", response_model=Dict[str, int])
async def get_water_stats(
    days: int = Query(30, ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    analytics_use_cases: AnalyticsUseCases = Depends(get_analytics_use_cases),
):
    """Get daily water consumption for the last N days"""
    stats = await analytics_use_cases.get_water_consumption_stats(user_id, days)
    return stats