from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.auth_schemas import ChangePasswordRequest, RegisterRequest, LoginRequest, TokenResponse, UpdateUserRequest, UserResponse
from ..dependencies import get_auth_use_cases, get_current_user_id
from ...application.use_cases.auth_use_cases import AuthUseCases

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Register a new user"""
    try:
        result = await auth_use_cases.register_user(
            email=request.email,
            username=request.username,
            password=request.password,
            name=request.name
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Login a user with email or username"""
    try:
        result = await auth_use_cases.login_user(
            email_or_username=request.email_or_username,
            password=request.password
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Get current user"""
    user = await auth_use_cases.get_current_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/me", response_model=UserResponse)
async def update_me(
    request: UpdateUserRequest,
    user_id: str = Depends(get_current_user_id),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases)
):
    """Update current user's details"""
    try:
        success = await auth_use_cases.update_user_details(
            user_id=user_id,
            name=request.name,
            email=request.email,
            username=request.username,
            height=request.height,
            weight=request.weight,
            gender=request.gender,
            birth_date=request.birth_date
        )
        if success:
            user = await auth_use_cases.get_current_user(user_id)
            return user
        # This part may not be reached if update fails, depends on repository implementation
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not update user details")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/me/change-password", response_model=dict)
async def change_password(
    request: ChangePasswordRequest,
    user_id: str = Depends(get_current_user_id),
    auth_use_cases: AuthUseCases = Depends(get_auth_use_cases),
):
    """Change current user's password"""
    try:
        success = await auth_use_cases.change_password(
            user_id=user_id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        if success:
            return {"message": "Password updated successfully"}
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not update password")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
