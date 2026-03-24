from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
from services.user_service import UserService
from deps import get_current_superuser, get_current_active_user
from models.user import User
from repositories.role_repository import RoleRepository
from core.exceptions import NotFoundException

router = APIRouter(prefix="/roles", tags=["roles"])

class RoleCreate(BaseModel):
    name: str
    description: str = None

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str

class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int

@router.post("/", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    role_repo = RoleRepository(db)
    role = role_repo.create(name=role_data.name, description=role_data.description)
    return role

@router.post("/assign", response_model=dict)
async def assign_role_to_user(
    assign_data: AssignRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    user_service = UserService(db)
    await user_service.assign_role(assign_data.user_id, assign_data.role_id)
    return {"message": "Role assigned successfully"}

@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    role_repo = RoleRepository(db)
    return role_repo.get_all()

@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    role_repo = RoleRepository(db)
    success = role_repo.delete(role_id)
    if not success:
        raise NotFoundException("Role not found")
    return {"message": "Role deleted successfully"}
