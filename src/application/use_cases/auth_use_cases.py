from typing import Optional
from datetime import timedelta
from ...domain.entities.user import UserEntity
from ...infrastructure.repositories.user_repository import UserRepository
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.config import settings


class AuthUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(
        self, email: str, username: str, password: str, name: str
    ) -> dict:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        existing_username = await self.user_repository.find_by_username(username)
        if existing_username:
            raise ValueError("Username already taken")
        
        # Create user
        password_hash = get_password_hash(password)
        user = UserEntity(
            email=email,
            username=username,
            password_hash=password_hash,
            name=name
        )
        
        user_id = await self.user_repository.create(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "username": username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "username": username,
                "name": name
            }
        }

    async def login_user(self, email_or_username: str, password: str) -> dict:
        """Login a user with email or username"""
        # Try to find user by email first
        user = await self.user_repository.find_by_email(email_or_username)
        
        # If not found by email, try username
        if not user:
            user = await self.user_repository.find_by_username(email_or_username)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "name": user.name
            }
        }

    async def get_current_user(self, user_id: str) -> Optional[dict]:
        """Get current user by ID"""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
