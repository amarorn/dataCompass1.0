"""
MongoDB implementation of User repository.
"""

from typing import List, Optional

from app.core.logging import LoggerMixin
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.database.models.user_model import UserModel


class MongoDBUserRepository(IUserRepository, LoggerMixin):
    """MongoDB implementation of User repository."""
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        try:
            model = UserModel.from_entity(user)
            await model.insert()
            self.logger.info(f"User {user.id} created successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            model = await UserModel.get(user_id)
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            model = await UserModel.find_one(
                UserModel.email == email
            )
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            model = await UserModel.find_one(
                UserModel.username == username
            )
            return model.to_entity() if model else None
        except Exception as e:
            self.logger.error(f"Error getting user by username {username}: {e}")
            return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        try:
            models = await UserModel.find().skip(skip).limit(limit).to_list()
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting users: {e}")
            return []
    
    async def update(self, user: User) -> User:
        """Update an existing user."""
        try:
            model = await UserModel.get(user.id)
            if not model:
                raise ValueError(f"User {user.id} not found")
            
            # Update fields
            model.email = user.email
            model.username = user.username
            model.full_name = user.full_name
            model.hashed_password = user.hashed_password
            model.is_active = user.is_active
            model.is_superuser = user.is_superuser
            model.updated_at = user.updated_at
            model.last_login = user.last_login
            
            await model.save()
            self.logger.info(f"User {user.id} updated successfully")
            return model.to_entity()
        except Exception as e:
            self.logger.error(f"Error updating user {user.id}: {e}")
            raise
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            model = await UserModel.get(user_id)
            if not model:
                return False
            
            await model.delete()
            self.logger.info(f"User {user_id} deleted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def get_active_users(self) -> List[User]:
        """Get active users."""
        try:
            models = await UserModel.find(
                UserModel.is_active == True
            ).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting active users: {e}")
            return []
    
    async def get_superusers(self) -> List[User]:
        """Get superusers."""
        try:
            models = await UserModel.find(
                UserModel.is_superuser == True
            ).to_list()
            
            return [model.to_entity() for model in models]
        except Exception as e:
            self.logger.error(f"Error getting superusers: {e}")
            return []
    
    async def count(self) -> int:
        """Get total number of users."""
        try:
            return await UserModel.count()
        except Exception as e:
            self.logger.error(f"Error counting users: {e}")
            return 0
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        try:
            count = await UserModel.count(UserModel.email == email)
            return count > 0
        except Exception as e:
            self.logger.error(f"Error checking user existence by email {email}: {e}")
            return False
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        try:
            count = await UserModel.count(UserModel.username == username)
            return count > 0
        except Exception as e:
            self.logger.error(f"Error checking user existence by username {username}: {e}")
            return False