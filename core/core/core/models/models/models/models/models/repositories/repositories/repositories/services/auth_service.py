from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from repositories.user_repository import UserRepository
from models.token import RefreshToken
from core.security import verify_password, decode_token, create_access_token, create_refresh_token
from core.exceptions import AuthException, NotFoundException

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register_user(self, email: str, username: str, password: str):
        if self.user_repo.get_by_email(email):
            raise AuthException("Email already registered")
        
        if self.user_repo.get_by_username(username):
            raise AuthException("Username already taken")
        
        user = self.user_repo.create(email, username, password)
        return user
    
    async def authenticate_user(self, username: str, password: str):
        user = self.user_repo.get_by_email(username)
        if not user:
            user = self.user_repo.get_by_username(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AuthException("Invalid token type")
            
            db_token = self.db.query(RefreshToken).filter(
                RefreshToken.token == refresh_token,
                RefreshToken.expires_at > datetime.utcnow()
            ).first()
            
            if not db_token:
                raise AuthException("Invalid or expired refresh token")
            
            new_access_token = create_access_token(data={"sub": payload.get("sub")})
            new_refresh_token = create_refresh_token(data={"sub": payload.get("sub")})
            
            db_token.token = new_refresh_token
            db_token.expires_at = datetime.utcnow() + timedelta(days=7)
            self.db.commit()
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token
            }
            
        except Exception as e:
            raise AuthException("Invalid refresh token")
    
    async def logout(self, refresh_token: str):
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        
        if db_token:
            self.db.delete(db_token)
            self.db.commit()
    
    async def save_refresh_token(self, user_id: int, token: str, expires_at: datetime):
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        self.db.commit()
