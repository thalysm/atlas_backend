from typing import List, Optional
from pymongo.database import Database
from bson import ObjectId
from ...domain.entities.workout_package import WorkoutPackageEntity


class WorkoutPackageRepository:
    def __init__(self, db: Database):
        self.collection = db["workout_packages"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.collection.create_index("user_id")
        self.collection.create_index("is_public")

    async def create(self, package: WorkoutPackageEntity) -> str:
        """Create a new workout package"""
        package_dict = package.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(package_dict)
        return str(result.inserted_id)

    async def find_by_id(self, package_id: str) -> Optional[WorkoutPackageEntity]:
        """Find package by ID"""
        package_data = self.collection.find_one({"_id": ObjectId(package_id)})
        if package_data:
            package_data["_id"] = str(package_data["_id"])  # CONVERTE PARA STR
            return WorkoutPackageEntity(**package_data)
        return None

    async def find_by_user(self, user_id: str) -> List[WorkoutPackageEntity]:
        """Find all packages by user"""
        packages = []
        for doc in self.collection.find({"user_id": user_id}):
            doc["_id"] = str(doc["_id"])  # CONVERTE PARA STR
            packages.append(WorkoutPackageEntity(**doc))
        return packages

    async def find_public(self) -> List[WorkoutPackageEntity]:
        """Find all public packages"""
        packages = []
        for doc in self.collection.find({"is_public": True}):
            doc["_id"] = str(doc["_id"])  # CONVERTE PARA STR
            packages.append(WorkoutPackageEntity(**doc))
        return packages

    async def update(self, package_id: str, package: WorkoutPackageEntity) -> bool:
        """Update a package"""
        package_dict = package.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.update_one(
            {"_id": ObjectId(package_id)}, {"$set": package_dict}
        )
        return result.modified_count > 0

    async def delete(self, package_id: str) -> bool:
        """Delete a package"""
        result = self.collection.delete_one({"_id": ObjectId(package_id)})
        return result.deleted_count > 0
