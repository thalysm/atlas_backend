from pydantic import BaseModel, Field

class LogWaterRequest(BaseModel):
    amount_ml: int = Field(..., gt=0)