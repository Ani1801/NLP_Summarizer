"""
Document Service — Manages document CRUD and ownership verification in MongoDB.

All document-related database operations go through this service.
Route handlers NEVER query the documents collection directly.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
from app.core.logging import logger


VALID_STATUSES = {"uploaded", "processing", "processed", "failed", "deleted"}


class DocumentService:

    @staticmethod
    async def create_document(db, user_id: str, filename: str, storage_key: str,
                               file_size: int = 0, file_type: str = "pdf") -> dict:
        """Insert a new document record and return it."""
        doc_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "_id": doc_id,
            "user_id": user_id,
            "filename": filename,          # sanitised storage filename
            "original_filename": filename, # raw name from the upload
            "storage_key": storage_key,
            "file_type": file_type,
            "file_size": file_size,
            "page_count": 0,
            "status": "uploaded",
            "created_at": now,
            "updated_at": now,
        }
        await db["audits"].update_one({"_id": doc_id}, {"$setOnInsert": doc}, upsert=True)
        logger.info(f"[DocumentService] Created document {doc_id} for user {user_id}")
        return doc

    @staticmethod
    async def get_document(db, document_id: str, user_id: str) -> dict:
        """Fetch a document and verify ownership. Raises 404 if not found or not owned."""
        doc = await db["audits"].find_one({"_id": document_id, "user_id": user_id})
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or you do not have access to it."
            )
        return doc

    @staticmethod
    async def update_status(db, document_id: str, new_status: str,
                             extra_fields: Optional[dict] = None) -> None:
        """Update a document's processing status."""
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        update = {"status": new_status, "updated_at": datetime.utcnow()}
        if extra_fields:
            update.update(extra_fields)
        await db["audits"].update_one({"_id": document_id}, {"$set": update})

    @staticmethod
    async def list_user_documents(db, user_id: str, limit: int = 100) -> list:
        """Return all documents belonging to a user, sorted newest first."""
        cursor = db["audits"].find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
