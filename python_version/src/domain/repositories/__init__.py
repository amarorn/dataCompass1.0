"""
Domain Repositories - Interfaces
"""

from .client_repository import IClientRepository
from .interaction_repository import IInteractionRepository
from .user_repository import IUserRepository

__all__ = [
    "IClientRepository",
    "IInteractionRepository",
    "IUserRepository"
]