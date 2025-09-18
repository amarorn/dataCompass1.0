"""
User entity - represents system users (admins, analysts).
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, validator


class User(BaseModel):
    """User entity for system authentication."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="User is active")
    is_superuser: bool = Field(default=False, description="User is superuser")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    @validator('username')
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()
    
    def update_password(self, hashed_password: str) -> None:
        """Update user password."""
        self.hashed_password = hashed_password
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, **kwargs) -> None:
        """Update user profile information."""
        allowed_fields = {'email', 'username', 'full_name'}
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        
        self.updated_at = datetime.utcnow()
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserInDB(User):
    """User in database with hashed password."""
    hashed_password: str