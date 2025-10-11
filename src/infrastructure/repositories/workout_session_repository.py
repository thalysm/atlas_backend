from typing import List, Optional
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
from ...domain.entities.workout_session import WorkoutSessionEntity


def convert_objectid_to_str(doc: dict) -> dict:
    """Converte o _id de ObjectId para string"""
    doc["_id"] = str(doc["_id"])
    return doc


class WorkoutSessionRepository:
    def __init__(self, db: Database):
        self.collection = db["workout_sessions"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.collection.create_index("user_id")
        self.collection.create_index("start_time")
        self.collection.create_index([("user_id", 1), ("start_time", -1)])

    async def create(self, session: WorkoutSessionEntity) -> str:
        """Create a new workout session"""
        session_dict = session.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(session_dict)
        return str(result.inserted_id)

    async def find_by_id(self, session_id: str) -> Optional[WorkoutSessionEntity]:
        """Find session by ID"""
        session_data = self.collection.find_one({"_id": ObjectId(session_id)})
        if session_data:
            return WorkoutSessionEntity(**convert_objectid_to_str(session_data))
        return None

    async def find_by_user(
        self, user_id: str, limit: int = 50, skip: int = 0
    ) -> List[WorkoutSessionEntity]:
        """Find sessions by user"""
        sessions = []
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("start_time", -1)
            .skip(skip)
            .limit(limit)
        )
        for doc in cursor:
            sessions.append(WorkoutSessionEntity(**convert_objectid_to_str(doc)))
        return sessions

    async def find_by_user_and_date_range(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[WorkoutSessionEntity]:
        """Find sessions by user and date range"""
        sessions = []
        cursor = self.collection.find(
            {
                "user_id": user_id,
                "start_time": {"$gte": start_date, "$lte": end_date},
            }
        ).sort("start_time", -1)
        for doc in cursor:
            sessions.append(WorkoutSessionEntity(**convert_objectid_to_str(doc)))
        return sessions

    async def update(self, session_id: str, session: WorkoutSessionEntity) -> bool:
        """Update a session"""
        session_dict = session.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.update_one(
            {"_id": ObjectId(session_id)}, {"$set": session_dict}
        )
        return result.modified_count > 0

    async def delete(self, session_id: str) -> bool:
        """Delete a session"""
        result = self.collection.delete_one({"_id": ObjectId(session_id)})
        return result.deleted_count > 0
