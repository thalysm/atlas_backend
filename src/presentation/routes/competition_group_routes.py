from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..schemas.competition_group_schemas import (
    CreateGroupRequest,
    JoinGroupRequest,
    GroupResponse,
    GroupDetailsResponse,
)
from ..dependencies import get_current_user_id
from ...core.database import get_database
from ...infrastructure.repositories.competition_group_repository import (
    CompetitionGroupRepository,
)
from ...infrastructure.repositories.user_repository import UserRepository
from ...infrastructure.repositories.workout_session_repository import (
    WorkoutSessionRepository,
)
from ...application.use_cases.competition_group_use_cases import (
    CompetitionGroupUseCases,
)

router = APIRouter(prefix="/groups", tags=["Competition Groups"])


def get_group_use_cases() -> CompetitionGroupUseCases:
    db = get_database()
    group_repository = CompetitionGroupRepository(db)
    user_repository = UserRepository(db)
    session_repository = WorkoutSessionRepository(db)
    return CompetitionGroupUseCases(
        group_repository, user_repository, session_repository
    )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_group(
    request: CreateGroupRequest,
    user_id: str = Depends(get_current_user_id),
    group_use_cases: CompetitionGroupUseCases = Depends(get_group_use_cases),
):
    """Create a new competition group"""
    try:
        result = await group_use_cases.create_group(
            user_id, request.name, request.description
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/join", response_model=dict)
async def join_group(
    request: JoinGroupRequest,
    user_id: str = Depends(get_current_user_id),
    group_use_cases: CompetitionGroupUseCases = Depends(get_group_use_cases),
):
    """Join a group using invite code"""
    try:
        await group_use_cases.join_group(user_id, request.invite_code)
        return {"message": "Successfully joined group"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[GroupResponse])
async def get_user_groups(
    user_id: str = Depends(get_current_user_id),
    group_use_cases: CompetitionGroupUseCases = Depends(get_group_use_cases),
):
    """Get all groups for current user"""
    groups = await group_use_cases.get_user_groups(user_id)
    return groups


@router.get("/{group_id}", response_model=GroupDetailsResponse)
async def get_group_details(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    group_use_cases: CompetitionGroupUseCases = Depends(get_group_use_cases),
):
    """Get group details with leaderboard"""
    try:
        group = await group_use_cases.get_group_details(group_id, user_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
            )
        return group
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{group_id}/leave", response_model=dict)
async def leave_group(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    group_use_cases: CompetitionGroupUseCases = Depends(get_group_use_cases),
):
    """Leave a group"""
    try:
        await group_use_cases.leave_group(group_id, user_id)
        return {"message": "Successfully left group"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{group_id}", response_model=dict)
async def delete_group(
    group_id: str,
    user_id: str = Depends(get_current_user_id),
    group_use_cases: CompetitionGroupUseCases = Depends(get_group_use_cases),
):
    """Delete a group (owner only)"""
    try:
        await group_use_cases.delete_group(group_id, user_id)
        return {"message": "Group deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
