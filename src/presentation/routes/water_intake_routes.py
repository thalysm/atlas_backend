from fastapi import APIRouter, Depends, status
from ..schemas.water_intake_schemas import LogWaterRequest
from ..dependencies import get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.water_intake_repository import WaterIntakeRepository
from ...application.use_cases.water_intake_use_cases import WaterIntakeUseCases

router = APIRouter(prefix="/water", tags=["Water Intake"])

def get_water_intake_use_cases() -> WaterIntakeUseCases:
    db = get_database()
    repo = WaterIntakeRepository(db)
    return WaterIntakeUseCases(repo)

@router.post("", status_code=status.HTTP_201_CREATED)
async def log_water_intake(
    request: LogWaterRequest,
    user_id: str = Depends(get_current_user_id),
    use_cases: WaterIntakeUseCases = Depends(get_water_intake_use_cases),
):
    await use_cases.log_water(user_id, request.amount_ml)
    return {"message": "Water intake logged successfully"}