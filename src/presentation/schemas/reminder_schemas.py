from pydantic import BaseModel, Field
from typing import Optional, List, Union, Literal
from datetime import datetime

class ReminderRequestBase(BaseModel):
    title: str = Field(..., min_length=1)
    time: str # HH:MM format
    frequency: Literal['daily', 'weekly', 'monthly']
    frequency_details: Optional[Union[List[int], int]] = None # List[0-6] for weekly, int(1-31) for monthly

class CreateReminderRequest(ReminderRequestBase):
    pass

class UpdateReminderRequest(ReminderRequestBase):
    title: Optional[str] = Field(None, min_length=1)
    time: Optional[str] = None
    frequency: Optional[Literal['daily', 'weekly', 'monthly']] = None
    frequency_details: Optional[Union[List[int], int, None]] = ... # Ellipsis significa que é opcional mas pode ser None

class ReminderResponse(BaseModel):
    id: str
    user_id: str
    title: str
    time: str
    frequency: str
    frequency_details: Optional[Union[List[int], int]] = None
    created_at: str
    completed: Optional[bool] = None # Only relevant for /today endpoint