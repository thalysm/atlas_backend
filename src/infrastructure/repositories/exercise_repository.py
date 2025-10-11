from typing import Optional, List
from pymongo.database import Database
from ...domain.entities.exercise import ExerciseEntity


class ExerciseRepository:
    def __init__(self, db: Database):
        self.collection = db["exercises"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.collection.create_index("name")
        self.collection.create_index("category")

    async def create(self, exercise: ExerciseEntity) -> str:
        """Create a new exercise"""
        exercise_dict = exercise.model_dump(by_alias=True, exclude={"id"})
        result = self.collection.insert_one(exercise_dict)
        return str(result.inserted_id)

    async def find_all(self) -> List[ExerciseEntity]:
        """Get all exercises"""
        exercises = []
        for doc in self.collection.find():
            exercises.append(ExerciseEntity(**doc))
        return exercises

    async def find_by_id(self, exercise_id: str) -> Optional[ExerciseEntity]:
        """Find exercise by ID"""
        from bson import ObjectId
        exercise_data = self.collection.find_one({"_id": ObjectId(exercise_id)})
        if exercise_data:
            return ExerciseEntity(**exercise_data)
        return None

    async def find_by_category(self, category: str) -> List[ExerciseEntity]:
        """Find exercises by category"""
        exercises = []
        for doc in self.collection.find({"category": category}):
            exercises.append(ExerciseEntity(**doc))
        return exercises
