from typing import Optional
from datetime import datetime, timedelta, date
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
            "height": user.height,
            "weight": user.weight,
            "gender": user.gender,
            "birth_date": user.birth_date.date() if user.birth_date else None,
            "created_at": user.created_at.isoformat()
        }

    async def update_user_details(self, user_id: str, name: str, email: str, username: str,
                                height: Optional[float], weight: Optional[float],
                                gender: Optional[str], birth_date: Optional[date]) -> bool:
        """Update user details"""
        current_user = await self.user_repository.find_by_id(user_id)
        if not current_user:
            raise ValueError("User not found")

        # Check if new email is already taken by another user
        if email.lower() != current_user.email.lower():
            existing_email = await self.user_repository.find_by_email(email)
            if existing_email:
                raise ValueError("Email already registered")

        # Check if new username is already taken by another user
        if username.lower() != current_user.username.lower():
            existing_username = await self.user_repository.find_by_username(username)
            if existing_username:
                raise ValueError("Username already taken")

        # Convert date to datetime if it exists
        birth_datetime = datetime.combine(birth_date, datetime.min.time()) if birth_date else None

        update_data = {
            "name": name,
            "email": email,
            "username": username,
            "height": height,
            "weight": weight,
            "gender": gender,
            "birth_date": birth_datetime,
            "updated_at": datetime.utcnow()
        }

        return await self.user_repository.update(user_id, update_data)

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Incorrect current password")

        new_password_hash = get_password_hash(new_password)
        update_data = {"password_hash": new_password_hash, "updated_at": datetime.utcnow()}

        return await self.user_repository.update(user_id, update_data)