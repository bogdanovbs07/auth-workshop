from typing import List, Optional
from fastapi import Depends, HTTPException, status
from core.security import decode_token
from models.user import User
from repositories.user_repository import UserRepository
from database import get_db
from sqlalchemy.orm import Session

async def has_permission(
    user: User,
    required_permission: str,
    db: Session
) -> bool:
    """Check if user has specific permission"""
    if user.is_superuser:
        return True
    
    for role in user.roles:
        for permission in role.permissions:
            if permission.name == required_permission:
                return True
    return False

async def check_permissions(
    token: str,
    required_scopes: List[str],
    db: Session
) -> User:
    """Validate token and check required scopes/permissions"""
    try:
        payload = decode_token(token)
        user_email = payload.get("sub")
        
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(user_email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        for scope in required_scopes:
            if not await has_permission(user, scope, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permission: {scope}"
                )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
