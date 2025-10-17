from ...domain.entities.weight_history import WeightHistoryEntity
from ...infrastructure.repositories.weight_history_repository import WeightHistoryRepository
from ...infrastructure.repositories.user_repository import UserRepository

class WeightHistoryUseCases:
    def __init__(self, weight_history_repository: WeightHistoryRepository, user_repository: UserRepository):
        self.weight_history_repository = weight_history_repository
        self.user_repository = user_repository

    async def log_weight(self, user_id: str, weight: float) -> str:
        # Log the new weight entry
        entry = WeightHistoryEntity(user_id=user_id, weight=weight)
        entry_id = await self.weight_history_repository.create(entry)

        # Update the user's current weight
        await self.user_repository.update(user_id, {"weight": weight})

        return entry_id