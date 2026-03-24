from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import get_db
from services.auth_service import AuthService
from core.config import settings
from core.security import create_access_token, create_refresh_token
from core.exceptions import AuthException

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.register_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password
    )
    
    access_token = create_access_token(data={"sub": user.email, "scopes": []})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Save refresh token to database
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await auth_service.save_refresh_token(user.id, refresh_token, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise AuthException("Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.email, "scopes": []})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Save refresh token to database
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await auth_service.save_refresh_token(user.id, refresh_token, expires_at)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    new_tokens = await auth_service.refresh_access_token(request.refresh_token)
    return new_tokens

@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    await auth_service.logout(request.refresh_token)
    return {"message": "Successfully logged out"}
