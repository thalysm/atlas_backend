from typing import List
from pymongo.database import Database
from datetime import datetime
from ...domain.entities.weight_history import WeightHistoryEntity

class WeightHistoryRepository:
    def __init__(self, db: Database):
        self.collection = db["weight_history"]
        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index([("user_id", 1), ("created_at", -1)])

    async def create(self, entry: WeightHistoryEntity) -> str:
        entry_dict = entry.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(entry_dict)
        return str(result.inserted_id)

    async def find_by_user_and_date_range(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[WeightHistoryEntity]:
        entries = []
        cursor = self.collection.find(
            {
                "user_id": user_id,
                "created_at": {"$gte": start_date, "$lte": end_date},
            }
        ).sort("created_at", 1)
        for doc in cursor:
            entries.append(WeightHistoryEntity(**doc))
        return entries