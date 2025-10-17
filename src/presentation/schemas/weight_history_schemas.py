from pydantic import BaseModel, Field

class LogWeightRequest(BaseModel):
    weight: float = Field(..., gt=0)