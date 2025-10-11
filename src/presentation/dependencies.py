from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from ..core.database import get_database
from ..core.security import decode_access_token, verify_admin_key
from ..infrastructure.repositories.user_repository import UserRepository
from ..application.use_cases.auth_use_cases import AuthUseCases


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Get current user ID from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def verify_admin(x_admin_key: Optional[str] = Header(None)) -> bool:
    """Verify admin access"""
    if not x_admin_key or not verify_admin_key(x_admin_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return True


def get_auth_use_cases() -> AuthUseCases:
    """Get auth use cases instance"""
    db = get_database()
    user_repository = UserRepository(db)
    return AuthUseCases(user_repository)
