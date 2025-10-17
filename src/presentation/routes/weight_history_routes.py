from fastapi import APIRouter, Depends, status
from ..schemas.weight_history_schemas import LogWeightRequest
from ..dependencies import get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.weight_history_repository import WeightHistoryRepository
from ...infrastructure.repositories.user_repository import UserRepository
from ...application.use_cases.weight_history_use_cases import WeightHistoryUseCases

router = APIRouter(prefix="/weight", tags=["Weight History"])

def get_weight_history_use_cases() -> WeightHistoryUseCases:
    db = get_database()
    weight_repo = WeightHistoryRepository(db)
    user_repo = UserRepository(db)
    return WeightHistoryUseCases(weight_repo, user_repo)

@router.post("", status_code=status.HTTP_201_CREATED)
async def log_weight(
    request: LogWeightRequest,
    user_id: str = Depends(get_current_user_id),
    use_cases: WeightHistoryUseCases = Depends(get_weight_history_use_cases),
):
    await use_cases.log_weight(user_id, request.weight)
    return {"message": "Weight logged successfully"}