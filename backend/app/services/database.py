import motor.motor_asyncio
from app.core.config import settings

# Initialize Database Connection
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DATABASE_NAME]
audits_collection = db["audits"]

async def save_audit(audit_data: dict) -> str:
    """
    Inserts an audit record into the 'audits' collection.
    user_id is kept as a string (UUID) for consistency with auth.
    """
    result = await audits_collection.insert_one(audit_data)
    return str(result.inserted_id)
