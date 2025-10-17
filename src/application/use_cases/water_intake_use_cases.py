from ...domain.entities.water_intake import WaterIntakeEntity
from ...infrastructure.repositories.water_intake_repository import WaterIntakeRepository

class WaterIntakeUseCases:
    def __init__(self, water_intake_repository: WaterIntakeRepository):
        self.water_intake_repository = water_intake_repository

    async def log_water(self, user_id: str, amount_ml: int) -> str:
        intake = WaterIntakeEntity(user_id=user_id, amount_ml=amount_ml)
        return await self.water_intake_repository.create(intake)