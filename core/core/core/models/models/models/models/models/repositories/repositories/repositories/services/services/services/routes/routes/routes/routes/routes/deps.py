from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from repositories.user_repository import UserRepository
from core.security import decode_token
from core.exceptions import AuthException, PermissionDenied
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False
)

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from token"""
    if not token:
        raise AuthException("Not authenticated")
    
    try:
        payload = decode_token(token)
        user_email = payload.get("sub")
        
        if not user_email:
            raise AuthException("Invalid token")
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(user_email)
        
        if not user:
            raise AuthException("User not found")
        
        return user
        
    except Exception as e:
        raise AuthException("Invalid authentication credentials")

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise PermissionDenied("Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current superuser"""
    if not current_user.is_superuser:
        raise PermissionDenied("Superuser privileges required")
    return current_user
