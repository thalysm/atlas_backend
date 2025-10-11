from pydantic import BaseModel, Field
from typing import Optional, List


class ExerciseInPackageRequest(BaseModel):
    exercise_id: str
    order: int
    notes: Optional[str] = None


class CreatePackageRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    exercises: List[ExerciseInPackageRequest]
    is_public: bool = False


class UpdatePackageRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    exercises: List[ExerciseInPackageRequest]
    is_public: bool = False


class PackageResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    exercises: List[dict]
    is_public: bool
    created_at: str
    updated_at: Optional[str] = None
