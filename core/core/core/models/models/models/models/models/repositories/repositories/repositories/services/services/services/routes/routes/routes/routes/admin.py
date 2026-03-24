from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from services.user_service import UserService
from deps import get_current_superuser
from models.user import User
from routes.users import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    user_service = UserService(db)
    users = await user_service.get_all_users(skip, limit)
    return users

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    user_service = UserService(db)
    await user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}
