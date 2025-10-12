from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email_or_username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    name: str
    created_at: str

class UpdateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    name: str = Field(..., min_length=1, max_length=100)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)