from typing import Optional
from pymongo.database import Database
from ...domain.entities.user import UserEntity


class UserRepository:
    def __init__(self, db: Database):
        self.collection = db["users"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.collection.create_index("email", unique=True)
        self.collection.create_index("username", unique=True)

    async def create(self, user: UserEntity) -> str:
        """Create a new user"""
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(user_dict)
        return str(result.inserted_id)

    async def find_by_email(self, email: str) -> Optional[UserEntity]:
        """Find user by email"""
        user_data = self.collection.find_one({"email": email})
        if user_data:
            return UserEntity(**user_data)
        return None

    async def find_by_username(self, username: str) -> Optional[UserEntity]:
        """Find user by username"""
        user_data = self.collection.find_one({"username": username})
        if user_data:
            return UserEntity(**user_data)
        return None

    async def find_by_id(self, user_id: str) -> Optional[UserEntity]:
        """Find user by ID"""
        from bson import ObjectId
        user_data = self.collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return UserEntity(**user_data)
        return None
