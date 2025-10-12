from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from datetime import datetime
from ..schemas.workout_session_schemas import (
    StartSessionRequest,
    UpdateSessionRequest,
    SessionResponse,
)
from ..dependencies import get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.workout_session_repository import (
    WorkoutSessionRepository,
)
from ...infrastructure.repositories.workout_package_repository import (
    WorkoutPackageRepository,
)
from ...infrastructure.repositories.exercise_repository import ExerciseRepository
from ...application.use_cases.workout_session_use_cases import WorkoutSessionUseCases

router = APIRouter(prefix="/sessions", tags=["Workout Sessions"])


def get_session_use_cases() -> WorkoutSessionUseCases:
    db = get_database()
    session_repository = WorkoutSessionRepository(db)
    package_repository = WorkoutPackageRepository(db)
    exercise_repository = ExerciseRepository(db)
    return WorkoutSessionUseCases(
        session_repository, package_repository, exercise_repository
    )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def start_session(
    request: StartSessionRequest,
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Start a new workout session"""
    try:
        session_id = await session_use_cases.start_session(user_id, request.package_id)
        return {"id": session_id, "message": "Session started successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[dict])
async def get_sessions(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Get all sessions for current user"""
    sessions = await session_use_cases.get_user_sessions(user_id, limit, skip)
    return sessions

@router.get("/all", response_model=List[dict])
async def get_all_sessions(
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Get all sessions for the current user"""
    sessions = await session_use_cases.get_all_user_sessions(user_id)
    return sessions

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Get session by ID"""
    session = await session_use_cases.get_session(session_id, user_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session


@router.put("/{session_id}", response_model=dict)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Update session with exercise data"""
    try:
        await session_use_cases.update_session(
            session_id, user_id, request.exercises
        )
        return {"message": "Session updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{session_id}/complete", response_model=dict)
async def complete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Complete a workout session"""
    try:
        await session_use_cases.complete_session(session_id, user_id)
        return {"message": "Session completed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{session_id}", response_model=dict)
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Cancel and delete a workout session"""
    try:
        await session_use_cases.delete_session(session_id, user_id)
        return {"message": "Workout session cancelled successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.post("/start-empty", response_model=dict, status_code=status.HTTP_201_CREATED)
async def start_empty_session(
    user_id: str = Depends(get_current_user_id),
    session_use_cases: WorkoutSessionUseCases = Depends(get_session_use_cases),
):
    """Start a new empty workout session"""
    try:
        session_id = await session_use_cases.start_empty_session(user_id)
        return {"id": session_id, "message": "Empty session started successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

