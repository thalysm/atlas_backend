from datetime import datetime
from typing import Optional, Union, Any
from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId compatible with Pydantic v2"""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: JsonSchemaValue, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema.update(type="string", example=str(ObjectId()))
        return json_schema

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    def __str__(self):
        return str(self)


class StrengthSet(BaseModel):
    set_number: int
    weight: float
    reps: int
    completed: bool = False


class CardioSet(BaseModel):
    duration_minutes: float
    distance: Optional[float] = None
    incline: Optional[float] = None
    speed: Optional[float] = None
    completed: bool = False


class ExerciseLog(BaseModel):
    exercise_id: str
    exercise_name: str
    type: str  # "strength" or "cardio"
    sets: list[Union[StrengthSet, CardioSet]] = []
    notes: Optional[str] = None


class WorkoutSessionEntity(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    package_id: str
    package_name: str
    exercises: list[ExerciseLog] = []
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    is_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
