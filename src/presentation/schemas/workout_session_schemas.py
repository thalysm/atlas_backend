from pydantic import BaseModel
from typing import Optional, List, Union


class StartSessionRequest(BaseModel):
    package_id: str


class StrengthSetData(BaseModel):
    set_number: int
    weight: float
    reps: int
    completed: bool = False


class CardioSetData(BaseModel):
    duration_minutes: float
    distance: Optional[float] = None
    incline: Optional[float] = None
    speed: Optional[float] = None
    completed: bool = False


class ExerciseLogData(BaseModel):
    exercise_id: str
    exercise_name: str
    type: str
    sets: List[Union[StrengthSetData, CardioSetData]]
    notes: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    exercises: List[dict]


class SessionResponse(BaseModel):
    id: str
    user_id: str
    package_id: str
    package_name: str
    exercises: List[dict]
    start_time: str
    end_time: Optional[str]
    duration_minutes: Optional[int]
    is_completed: bool
    total_calories: Optional[float] = None
