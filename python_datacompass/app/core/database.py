"""
Database connection and configuration.
"""

import asyncio
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """MongoDB database manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """Connect to MongoDB."""
        try:
            logger.info("Connecting to MongoDB...")
            
            self.client = AsyncIOMotorClient(
                settings.mongodb_uri,
                maxPoolSize=10,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=45000,
            )
            
            # Test connection
            await self.client.admin.command("ping")
            
            self.database = self.client[settings.database_name]
            
            logger.info(f"Connected to MongoDB database: {settings.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> dict:
        """Check database health."""
        try:
            if not self.client or not self.database:
                return {
                    "status": "disconnected",
                    "database": "unknown",
                    "connected": False
                }
            
            # Ping the database
            await self.client.admin.command("ping")
            
            # Get database stats
            stats = await self.database.command("dbStats")
            
            return {
                "status": "connected",
                "database": self.database.name,
                "connected": True,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0)
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "error",
                "database": self.database.name if self.database else "unknown",
                "connected": False,
                "error": str(e)
            }
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if not self.database:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """Get database dependency for FastAPI."""
    return db_manager.get_database()


async def init_database() -> None:
    """Initialize database connection."""
    await db_manager.connect()


async def close_database() -> None:
    """Close database connection."""
    await db_manager.disconnect()