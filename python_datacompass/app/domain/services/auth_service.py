"""
Authentication service - business logic for user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional

from app.core.logging import LoggerMixin
from app.core.security import create_access_token, verify_password, get_password_hash
from app.domain.entities.user import User, UserCreate, UserLogin
from app.domain.repositories.user_repository import IUserRepository


class AuthService(LoggerMixin):
    """Service for user authentication and authorization."""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = await self.user_repository.get_by_username(username)
        
        if not user:
            self.logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        if not user.is_active:
            self.logger.warning(f"Authentication failed: user {username} is inactive")
            return None
        
        if not verify_password(password, user.hashed_password):
            self.logger.warning(f"Authentication failed: invalid password for user {username}")
            return None
        
        # Update last login
        user.update_last_login()
        await self.user_repository.update(user)
        
        self.logger.info(f"User {username} authenticated successfully")
        return user
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        if await self.user_repository.exists_by_email(user_create.email):
            raise ValueError("User with this email already exists")
        
        if await self.user_repository.exists_by_username(user_create.username):
            raise ValueError("User with this username already exists")
        
        # Create user
        user = User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=get_password_hash(user_create.password)
        )
        
        created_user = await self.user_repository.create(user)
        
        self.logger.info(f"User {created_user.username} created successfully")
        return created_user
    
    async def get_user_by_token(self, token: str) -> Optional[User]:
        """Get user by JWT token."""
        from app.core.security import verify_token
        
        payload = verify_token(token)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        return await self.user_repository.get_by_username(username)
    
    def create_access_token_for_user(self, user: User) -> str:
        """Create access token for a user."""
        return create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
    
    async def change_password(
        self, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password."""
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Update password
        user.update_password(get_password_hash(new_password))
        await self.user_repository.update(user)
        
        self.logger.info(f"Password changed for user {user.username}")
        return True
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        user.deactivate()
        await self.user_repository.update(user)
        
        self.logger.info(f"User {user.username} deactivated")
        return True
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        user.activate()
        await self.user_repository.update(user)
        
        self.logger.info(f"User {user.username} activated")
        return True
    
    def is_superuser(self, user: User) -> bool:
        """Check if user is a superuser."""
        return user.is_superuser
    
    def can_access_admin_features(self, user: User) -> bool:
        """Check if user can access admin features."""
        return user.is_active and (user.is_superuser or user.email.endswith("@datacompass.com"))