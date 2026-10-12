from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logging import logger

import os
_mongo_client: AsyncIOMotorClient = None

def get_mongo_client() -> AsyncIOMotorClient:
    global _mongo_client
    uri = os.getenv("MONGO_URI") or settings.MONGO_URI
    if _mongo_client is None or getattr(_mongo_client, "_target_uri", None) != uri:
        _mongo_client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1,
        )
        setattr(_mongo_client, "_target_uri", uri)
    return _mongo_client

def get_database():
    client = get_mongo_client()
    db_name = os.getenv("DATABASE_NAME") or settings.DATABASE_NAME
    return client[db_name]

async def init_db_indexes():
    """Initializes necessary indexes on MongoDB collections."""
    try:
        db = get_database()
        # Create unique index on users.email
        await db["users"].create_index("email", unique=True)
        # Create index on audits.user_id and audits.created_at
        await db["audits"].create_index("user_id")
        await db["audits"].create_index([("created_at", -1)])
        # Sparse unique index on google_sub — allows multiple docs with null/absent google_sub
        # sparse=True means documents without the field are excluded from the index
        await db["users"].create_index("google_sub", unique=True, sparse=True)
        logger.info("Database indexes initialized successfully.")
    except Exception as e:
        logger.warning(f"Database index initialization warning: {e}")
