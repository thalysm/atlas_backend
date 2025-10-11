from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas.workout_package_schemas import (
    CreatePackageRequest,
    UpdatePackageRequest,
    PackageResponse,
)
from ..dependencies import get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.workout_package_repository import (
    WorkoutPackageRepository,
)
from ...application.use_cases.workout_package_use_cases import WorkoutPackageUseCases

router = APIRouter(prefix="/packages", tags=["Workout Packages"])


def get_package_use_cases() -> WorkoutPackageUseCases:
    db = get_database()
    package_repository = WorkoutPackageRepository(db)
    return WorkoutPackageUseCases(package_repository)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_package(
    request: CreatePackageRequest,
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Create a new workout package"""
    exercises = [ex.model_dump() for ex in request.exercises]
    package_id = await package_use_cases.create_package(
        user_id=user_id,
        name=request.name,
        description=request.description,
        exercises=exercises,
        is_public=request.is_public,
    )
    return {"id": package_id, "message": "Package created successfully"}


@router.get("/", response_model=List[PackageResponse])
async def get_user_packages(
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Get all packages for current user"""
    packages = await package_use_cases.get_user_packages(user_id)
    return packages


@router.get("/public", response_model=List[PackageResponse])
async def get_public_packages(
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Get all public packages"""
    packages = await package_use_cases.get_public_packages()
    return packages


@router.get("/{package_id}", response_model=PackageResponse)
async def get_package(
    package_id: str,
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Get package by ID"""
    package = await package_use_cases.get_package_by_id(package_id)
    if not package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    return package


@router.put("/{package_id}", response_model=dict)
async def update_package(
    package_id: str,
    request: UpdatePackageRequest,
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Update a workout package"""
    try:
        exercises = [ex.model_dump() for ex in request.exercises]
        await package_use_cases.update_package(
            package_id=package_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            exercises=exercises,
            is_public=request.is_public,
        )
        return {"message": "Package updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{package_id}", response_model=dict)
async def delete_package(
    package_id: str,
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Delete a workout package"""
    try:
        await package_use_cases.delete_package(package_id, user_id)
        return {"message": "Package deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{package_id}/copy", response_model=dict, status_code=status.HTTP_201_CREATED)
async def copy_package(
    package_id: str,
    user_id: str = Depends(get_current_user_id),
    package_use_cases: WorkoutPackageUseCases = Depends(get_package_use_cases),
):
    """Copy a public package to user's account"""
    try:
        new_package_id = await package_use_cases.copy_package(package_id, user_id)
        return {"id": new_package_id, "message": "Package copied successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
