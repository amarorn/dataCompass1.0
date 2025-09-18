"""
User Repository Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..entities.user import User, UserRole


class IUserRepository(ABC):
    """Interface for user repository"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key"""
        pass
    
    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[User]:
        """Get all users with pagination and filters"""
        pass
    
    @abstractmethod
    async def update(self, user_id: str, user: User) -> Optional[User]:
        """Update user information"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user"""
        pass
    
    @abstractmethod
    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by role"""
        pass
    
    @abstractmethod
    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get active users"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count users with optional filters"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        pass
    
    @abstractmethod
    async def increment_login_attempts(self, user_id: str) -> int:
        """Increment login attempts and return new count"""
        pass
    
    @abstractmethod
    async def reset_login_attempts(self, user_id: str) -> bool:
        """Reset login attempts to zero"""
        pass
    
    @abstractmethod
    async def lock_user(self, user_id: str, until: datetime) -> bool:
        """Lock user until specified time"""
        pass
    
    @abstractmethod
    async def unlock_user(self, user_id: str) -> bool:
        """Unlock user account"""
        pass
    
    @abstractmethod
    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password hash"""
        pass
    
    @abstractmethod
    async def verify_user(self, user_id: str) -> bool:
        """Mark user as verified"""
        pass
    
    @abstractmethod
    async def generate_api_key(self, user_id: str) -> Optional[str]:
        """Generate new API key for user"""
        pass
    
    @abstractmethod
    async def revoke_api_key(self, user_id: str) -> bool:
        """Revoke user's API key"""
        pass