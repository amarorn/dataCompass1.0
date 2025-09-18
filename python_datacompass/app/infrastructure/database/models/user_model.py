"""
User MongoDB model using Beanie.
"""

from datetime import datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import EmailStr, Field


class UserModel(Document):
    """MongoDB model for User entity."""
    
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "username",
            "is_active",
            "is_superuser"
        ]
    
    @classmethod
    def from_entity(cls, user) -> "UserModel":
        """Create model from entity."""
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
    
    def to_entity(self):
        """Convert model to entity."""
        from app.domain.entities.user import User
        
        return User(
            id=str(self.id),
            email=self.email,
            username=self.username,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login=self.last_login
        )