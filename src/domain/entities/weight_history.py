from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .user import PyObjectId

class WeightHistoryEntity(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    weight: float = Field(..., gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
    }