from pydantic import BaseModel, Field
from typing import Optional, List


class CreateExerciseRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: str
    type: str = Field(..., pattern="^(strength|cardio)$")
    muscle_groups: List[str] = []
    equipment: Optional[str] = None


class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    type: str
    muscle_groups: List[str]
    equipment: Optional[str]
