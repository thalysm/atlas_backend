from pydantic import BaseModel, Field
from typing import Optional, List


class CreateGroupRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class JoinGroupRequest(BaseModel):
    invite_code: str


class GroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    member_count: int
    invite_code: str
    created_at: str


class GroupMemberResponse(BaseModel):
    user_id: str
    username: str
    workout_count: int
    joined_at: str


class GroupDetailsResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    invite_code: str
    members: List[GroupMemberResponse]
    created_at: str
