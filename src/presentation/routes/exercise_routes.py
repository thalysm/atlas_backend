from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas.exercise_schemas import CreateExerciseRequest, ExerciseResponse
from ..dependencies import verify_admin, get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.exercise_repository import ExerciseRepository
from ...application.use_cases.exercise_use_cases import ExerciseUseCases

router = APIRouter(prefix="/exercises", tags=["Exercises"])


def get_exercise_use_cases() -> ExerciseUseCases:
    db = get_database()
    exercise_repository = ExerciseRepository(db)
    return ExerciseUseCases(exercise_repository)


@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin)],
)
async def create_exercise(
    request: CreateExerciseRequest,
    exercise_use_cases: ExerciseUseCases = Depends(get_exercise_use_cases),
):
    """Create a new exercise (admin only)"""
    exercise_id = await exercise_use_cases.create_exercise(
        name=request.name,
        description=request.description,
        category=request.category,
        type=request.type,
        muscle_groups=request.muscle_groups,
        equipment=request.equipment,
    )
    return {"id": exercise_id, "message": "Exercise created successfully"}


@router.get("/", response_model=List[ExerciseResponse])
async def get_exercises(
    category: str = None,
    user_id: str = Depends(get_current_user_id),
    exercise_use_cases: ExerciseUseCases = Depends(get_exercise_use_cases),
):
    """Get all exercises or filter by category"""
    if category:
        exercises = await exercise_use_cases.get_exercises_by_category(category)
    else:
        exercises = await exercise_use_cases.get_all_exercises()
    return exercises


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    user_id: str = Depends(get_current_user_id),
    exercise_use_cases: ExerciseUseCases = Depends(get_exercise_use_cases),
):
    """Get exercise by ID"""
    exercise = await exercise_use_cases.get_exercise_by_id(exercise_id)
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise
