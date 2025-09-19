"""
User Entity
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator
import re


class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    ANALYST = "ANALYST"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"


class User(BaseModel):
    """User entity for system authentication and authorization"""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: str
    password_hash: str  # Never store plain passwords
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    is_verified: bool = False
    
    # Permissions
    permissions: List[str] = Field(default_factory=list)
    
    # WhatsApp integration
    whatsapp_enabled: bool = False
    whatsapp_number: Optional[str] = None
    
    # Security
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    
    # API access
    api_key: Optional[str] = None
    api_key_created_at: Optional[datetime] = None
    api_rate_limit: int = 1000  # requests per hour
    
    # Preferences
    preferences: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "whatsapp": False,
        "dashboard": True
    })
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens and underscores')
        return v.lower()
    
    @field_validator('whatsapp_number')
    @classmethod
    def validate_whatsapp_number(cls, v: Optional[str]) -> Optional[str]:
        """Validate WhatsApp number if provided"""
        if v is None:
            return v
        
        clean_number = re.sub(r'\D', '', v)
        if len(clean_number) < 10 or len(clean_number) > 15:
            raise ValueError('Invalid WhatsApp number format')
        
        return clean_number
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        # Admins have all permissions
        if self.role == UserRole.ADMIN:
            return True
        
        # Check role-based permissions
        role_permissions = {
            UserRole.MANAGER: [
                "view_analytics", "export_data", "manage_clients", 
                "send_messages", "view_reports"
            ],
            UserRole.ANALYST: [
                "view_analytics", "export_data", "view_reports"
            ],
            UserRole.OPERATOR: [
                "view_clients", "send_messages", "view_basic_analytics"
            ],
            UserRole.VIEWER: [
                "view_basic_analytics", "view_reports"
            ]
        }
        
        if permission in role_permissions.get(self.role, []):
            return True
        
        # Check explicit permissions
        return permission in self.permissions
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_manager(self) -> bool:
        """Check if user is manager or above"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def can_send_messages(self) -> bool:
        """Check if user can send WhatsApp messages"""
        return self.has_permission("send_messages")
    
    def can_view_analytics(self) -> bool:
        """Check if user can view analytics"""
        return self.has_permission("view_analytics") or self.has_permission("view_basic_analytics")
    
    def can_manage_clients(self) -> bool:
        """Check if user can manage clients"""
        return self.has_permission("manage_clients")
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def record_login_attempt(self, success: bool) -> None:
        """Record a login attempt"""
        if success:
            self.login_attempts = 0
            self.last_login = datetime.utcnow()
            self.locked_until = None
        else:
            self.login_attempts += 1
            # Lock account after 5 failed attempts
            if self.login_attempts >= 5:
                self.locked_until = datetime.utcnow().replace(
                    hour=datetime.utcnow().hour + 1
                )
        
        self.updated_at = datetime.utcnow()
    
    def update_password_hash(self, password_hash: str) -> None:
        """Update password hash"""
        self.password_hash = password_hash
        self.password_changed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def generate_api_key(self) -> str:
        """Generate new API key"""
        from secrets import token_urlsafe
        self.api_key = token_urlsafe(32)
        self.api_key_created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return self.api_key
    
    def revoke_api_key(self) -> None:
        """Revoke API key"""
        self.api_key = None
        self.api_key_created_at = None
        self.updated_at = datetime.utcnow()
    
    def update_preference(self, key: str, value: Any) -> None:
        """Update user preference"""
        self.preferences[key] = value
        self.updated_at = datetime.utcnow()
    
    def update_notification_setting(self, channel: str, enabled: bool) -> None:
        """Update notification setting"""
        if channel in self.notification_settings:
            self.notification_settings[channel] = enabled
            self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert to dictionary for serialization"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "permissions": self.permissions,
            "whatsapp_enabled": self.whatsapp_enabled,
            "whatsapp_number": self.whatsapp_number,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "preferences": self.preferences,
            "notification_settings": self.notification_settings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data.update({
                "api_key": self.api_key,
                "api_key_created_at": self.api_key_created_at.isoformat() if self.api_key_created_at else None,
                "api_rate_limit": self.api_rate_limit,
                "login_attempts": self.login_attempts,
                "locked_until": self.locked_until.isoformat() if self.locked_until else None,
                "is_locked": self.is_locked()
            })
        
        return data
    
    class Config:
        use_enum_values = False
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
