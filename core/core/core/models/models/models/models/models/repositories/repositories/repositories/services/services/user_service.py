from sqlalchemy.orm import Session
from typing import Optional, List

from repositories.user_repository import UserRepository
from repositories.role_repository import RoleRepository
from core.exceptions import NotFoundException, ConflictException

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
    
    async def get_user_by_id(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user
    
    async def update_user(self, user_id: int, **kwargs):
        user = self.user_repo.update(user_id, **kwargs)
        if not user:
            raise NotFoundException("User not found")
        return user
    
    async def delete_user(self, user_id: int):
        success = self.user_repo.delete(user_id)
        if not success:
            raise NotFoundException("User not found")
    
    async def get_all_users(self, skip: int = 0, limit: int = 100):
        return self.user_repo.get_all(skip, limit)
    
    async def assign_role(self, user_id: int, role_id: int):
        user = self.user_repo.get_by_id(user_id)
        role = self.role_repo.get_by_id(role_id)
        
        if not user:
            raise NotFoundException("User not found")
        if not role:
            raise NotFoundException("Role not found")
        
        if role not in user.roles:
            user.roles.append(role)
            self.db.commit()
    
    async def remove_role(self, user_id: int, role_id: int):
        user = self.user_repo.get_by_id(user_id)
        role = self.role_repo.get_by_id(role_id)
        
        if not user:
            raise NotFoundException("User not found")
        if not role:
            raise NotFoundException("Role not found")
        
        if role in user.roles:
            user.roles.remove(role)
            self.db.commit()
