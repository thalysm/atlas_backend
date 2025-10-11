from typing import List, Optional
from ...domain.entities.exercise import ExerciseEntity
from ...infrastructure.repositories.exercise_repository import ExerciseRepository


class ExerciseUseCases:
    def __init__(self, exercise_repository: ExerciseRepository):
        self.exercise_repository = exercise_repository

    async def create_exercise(
        self,
        name: str,
        description: Optional[str],
        category: str,
        type: str,
        muscle_groups: List[str],
        equipment: Optional[str],
    ) -> str:
        """Create a new exercise (admin only)"""
        exercise = ExerciseEntity(
            name=name,
            description=description,
            category=category,
            type=type,
            muscle_groups=muscle_groups,
            equipment=equipment,
        )
        return await self.exercise_repository.create(exercise)

    async def get_all_exercises(self) -> List[dict]:
        """Get all exercises"""
        exercises = await self.exercise_repository.find_all()
        return [
            {
                "id": str(ex.id),
                "name": ex.name,
                "description": ex.description,
                "category": ex.category,
                "type": ex.type,
                "muscle_groups": ex.muscle_groups,
                "equipment": ex.equipment,
            }
            for ex in exercises
        ]

    async def get_exercise_by_id(self, exercise_id: str) -> Optional[dict]:
        """Get exercise by ID"""
        exercise = await self.exercise_repository.find_by_id(exercise_id)
        if not exercise:
            return None
        return {
            "id": str(exercise.id),
            "name": exercise.name,
            "description": exercise.description,
            "category": exercise.category,
            "type": exercise.type,
            "muscle_groups": exercise.muscle_groups,
            "equipment": exercise.equipment,
        }

    async def get_exercises_by_category(self, category: str) -> List[dict]:
        """Get exercises by category"""
        exercises = await self.exercise_repository.find_by_category(category)
        return [
            {
                "id": str(ex.id),
                "name": ex.name,
                "description": ex.description,
                "category": ex.category,
                "type": ex.type,
                "muscle_groups": ex.muscle_groups,
                "equipment": ex.equipment,
            }
            for ex in exercises
        ]
