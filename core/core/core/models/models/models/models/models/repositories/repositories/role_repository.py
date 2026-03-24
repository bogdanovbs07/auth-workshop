from sqlalchemy.orm import Session
from models.role import Role
from models.permission import Permission
from typing import Optional, List

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()
    
    def create(self, name: str, description: str = None) -> Role:
        role = Role(name=name, description=description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def add_permission(self, role_id: int, permission_id: int) -> Optional[Role]:
        role = self.get_by_id(role_id)
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if role and permission:
            role.permissions.append(permission)
            self.db.commit()
            self.db.refresh(role)
        return role
    
    def get_all(self) -> List[Role]:
        return self.db.query(Role).all()
    
    def delete(self, role_id: int) -> bool:
        role = self.get_by_id(role_id)
        if role:
            self.db.delete(role)
            self.db.commit()
            return True
        return False
