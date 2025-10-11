from typing import List, Optional
from datetime import datetime
from ...domain.entities.workout_package import WorkoutPackageEntity, ExerciseInPackage
from ...infrastructure.repositories.workout_package_repository import WorkoutPackageRepository


class WorkoutPackageUseCases:
    def __init__(self, package_repository: WorkoutPackageRepository):
        self.package_repository = package_repository

    async def create_package(
        self,
        user_id: str,
        name: str,
        description: Optional[str],
        exercises: List[dict],
        is_public: bool = False,
    ) -> str:
        """Create a new workout package"""
        exercise_list = [
            ExerciseInPackage(
                exercise_id=ex["exercise_id"], order=ex["order"], notes=ex.get("notes")
            )
            for ex in exercises
        ]

        package = WorkoutPackageEntity(
            user_id=user_id,
            name=name,
            description=description,
            exercises=exercise_list,
            is_public=is_public,
        )

        return await self.package_repository.create(package)

    async def get_user_packages(self, user_id: str) -> List[dict]:
        """Get all packages for a user"""
        packages = await self.package_repository.find_by_user(user_id)
        return [
            {
                "id": str(pkg.id),
                "user_id": pkg.user_id,
                "name": pkg.name,
                "description": pkg.description,
                "exercises": [
                    {
                        "exercise_id": ex.exercise_id,
                        "order": ex.order,
                        "notes": ex.notes,
                    }
                    for ex in pkg.exercises
                ],
                "is_public": pkg.is_public,
                "created_at": pkg.created_at.isoformat(),
                "updated_at": pkg.updated_at.isoformat(),
            }
            for pkg in packages
        ]

    async def get_package_by_id(self, package_id: str) -> Optional[dict]:
        """Get package by ID"""
        package = await self.package_repository.find_by_id(package_id)
        if not package:
            return None
        return {
            "id": str(package.id),
            "user_id": package.user_id,
            "name": package.name,
            "description": package.description,
            "exercises": [
                {
                    "exercise_id": ex.exercise_id,
                    "order": ex.order,
                    "notes": ex.notes,
                }
                for ex in package.exercises
            ],
            "is_public": package.is_public,
            "created_at": package.created_at.isoformat(),
            "updated_at": package.updated_at.isoformat(),
        }

    async def get_public_packages(self) -> List[dict]:
        """Get all public packages"""
        packages = await self.package_repository.find_public()
        return [
            {
                "id": str(pkg.id),
                "user_id": pkg.user_id,
                "name": pkg.name,
                "description": pkg.description,
                "exercises": [
                    {
                        "exercise_id": ex.exercise_id,
                        "order": ex.order,
                        "notes": ex.notes,
                    }
                    for ex in pkg.exercises
                ],
                "is_public": pkg.is_public,
                "created_at": pkg.created_at.isoformat(),
            }
            for pkg in packages
        ]

    async def update_package(
        self,
        package_id: str,
        user_id: str,
        name: str,
        description: Optional[str],
        exercises: List[dict],
        is_public: bool,
    ) -> bool:
        """Update a workout package"""
        # Verify ownership
        existing = await self.package_repository.find_by_id(package_id)
        if not existing or existing.user_id != user_id:
            raise ValueError("Package not found or unauthorized")

        exercise_list = [
            ExerciseInPackage(
                exercise_id=ex["exercise_id"], order=ex["order"], notes=ex.get("notes")
            )
            for ex in exercises
        ]

        package = WorkoutPackageEntity(
            user_id=user_id,
            name=name,
            description=description,
            exercises=exercise_list,
            is_public=is_public,
            created_at=existing.created_at,
            updated_at=datetime.utcnow(),
        )

        return await self.package_repository.update(package_id, package)

    async def delete_package(self, package_id: str, user_id: str) -> bool:
        """Delete a workout package"""
        # Verify ownership
        existing = await self.package_repository.find_by_id(package_id)
        if not existing or existing.user_id != user_id:
            raise ValueError("Package not found or unauthorized")

        return await self.package_repository.delete(package_id)

    async def copy_package(self, package_id: str, user_id: str) -> str:
        """Copy a public package to user's account"""
        original = await self.package_repository.find_by_id(package_id)
        if not original:
            raise ValueError("Package not found")

        if not original.is_public and original.user_id != user_id:
            raise ValueError("Cannot copy private package")

        new_package = WorkoutPackageEntity(
            user_id=user_id,
            name=f"{original.name} (Cópia)",
            description=original.description,
            exercises=original.exercises,
            is_public=False,
        )

        return await self.package_repository.create(new_package)
