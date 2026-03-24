from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from models.role import role_permissions

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)  # create, read, update, delete
    
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
