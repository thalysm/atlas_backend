from typing import List, Optional
from pymongo.database import Database
from bson import ObjectId
import secrets
from ...domain.entities.competition_group import CompetitionGroupEntity, GroupMember


class CompetitionGroupRepository:
    def __init__(self, db: Database):
        self.collection = db["competition_groups"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.collection.create_index("owner_id")
        self.collection.create_index("invite_code", unique=True)
        self.collection.create_index("members.user_id")

    def _generate_invite_code(self) -> str:
        """Generate a unique invite code"""
        return secrets.token_urlsafe(8)

    async def create(self, group: CompetitionGroupEntity) -> str:
        """Create a new competition group"""
        # Generate unique invite code
        while True:
            invite_code = self._generate_invite_code()
            existing = self.collection.find_one({"invite_code": invite_code})
            if not existing:
                group.invite_code = invite_code
                break

        group_dict = group.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(group_dict)
        return str(result.inserted_id)

    async def find_by_id(self, group_id: str) -> Optional[CompetitionGroupEntity]:
        """Find group by ID"""
        group_data = self.collection.find_one({"_id": ObjectId(group_id)})
        if group_data:
            return CompetitionGroupEntity(**group_data)
        return None

    async def find_by_invite_code(
        self, invite_code: str
    ) -> Optional[CompetitionGroupEntity]:
        """Find group by invite code"""
        group_data = self.collection.find_one({"invite_code": invite_code})
        if group_data:
            return CompetitionGroupEntity(**group_data)
        return None

    async def find_by_user(self, user_id: str) -> List[CompetitionGroupEntity]:
        """Find all groups where user is a member"""
        groups = []
        cursor = self.collection.find({"members.user_id": user_id})
        for doc in cursor:
            groups.append(CompetitionGroupEntity(**doc))
        return groups

    async def update(self, group_id: str, group: CompetitionGroupEntity) -> bool:
        """Update a group"""
        group_dict = group.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.update_one(
            {"_id": ObjectId(group_id)}, {"$set": group_dict}
        )
        return result.modified_count > 0

    async def delete(self, group_id: str) -> bool:
        """Delete a group"""
        result = self.collection.delete_one({"_id": ObjectId(group_id)})
        return result.deleted_count > 0
