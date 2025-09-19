"""
User repository interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.user import User


class IUserRepository(ABC):
    """User repository interface."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        pass
    
    @abstractmethod
    async def get_active_users(self) -> List[User]:
        """Get active users."""
        pass
    
    @abstractmethod
    async def get_superusers(self) -> List[User]:
        """Get superusers."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Get total number of users."""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        pass