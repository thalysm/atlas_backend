from typing import Any, Dict, List, Optional
from pymongo.database import Database
from bson import ObjectId
from ...domain.entities.reminder import ReminderEntity
from datetime import datetime


class ReminderRepository:
    def __init__(self, db: Database):
        self.collection = db["reminders"]
        self.collection.create_index([("user_id", 1), ("created_at", -1)])

    async def create(self, reminder: ReminderEntity) -> str:
        reminder_dict = reminder.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(reminder_dict)
        return str(result.inserted_id)

    async def find_by_user(self, user_id: str) -> List[ReminderEntity]:
        reminders = []
        cursor = self.collection.find({"user_id": user_id}).sort("time", 1)
        for doc in cursor:
            reminders.append(ReminderEntity(**doc))
        return reminders

    async def find_by_id(self, reminder_id: str) -> Optional[ReminderEntity]:
        reminder_data = self.collection.find_one({"_id": ObjectId(reminder_id)})
        if reminder_data:
            return ReminderEntity(**reminder_data)
        return None

    async def delete(self, reminder_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(reminder_id)})
        return result.deleted_count > 0

    async def update(self, reminder_id: str, reminder_update_data: Dict[str, Any]) -> bool:
        # Add updated_at timestamp automatically
        reminder_update_data["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(reminder_id)},
            {"$set": reminder_update_data}
        )
        return result.modified_count > 0