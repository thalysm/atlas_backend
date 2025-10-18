from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from .user import PyObjectId

class ReminderEntity(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    title: str
    time: str  # Armazenado como string "HH:MM"
    frequency: str  # 'daily', 'weekly', 'monthly'
    frequency_details: Optional[Union[List[int], int]] = None # List[0-6] for weekly, int(1-31) for monthly
    last_completed_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {PyObjectId: str},
    }