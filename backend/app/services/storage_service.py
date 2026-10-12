"""
StorageService — Abstract storage layer for uploaded PDFs.

Currently uses local filesystem (backend/uploads/).
The interface is designed so that switching to S3/Azure Blob Storage
only requires changing this service — no route handler changes needed.
"""

import os
import shutil
import uuid
from pathlib import Path
from app.core.config import settings


class StorageService:
    def __init__(self):
        # Resolve absolute uploads path relative to this file's location
        self._base_dir = Path(__file__).parent.parent.parent / settings.UPLOAD_DIR
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _storage_key(self, document_id: str, extension: str = "pdf") -> str:
        """Generate a safe, deterministic storage key for a document."""
        return f"{document_id}.{extension}"

    def save(self, file_bytes: bytes, document_id: str, extension: str = "pdf") -> str:
        """
        Save file bytes to local storage.
        Returns the storage_key (relative path used to retrieve later).
        """
        key = self._storage_key(document_id, extension)
        dest = self._base_dir / key
        with open(dest, "wb") as f:
            f.write(file_bytes)
        return key

    def get_path(self, storage_key: str) -> Path:
        """Return the absolute Path for a storage_key."""
        return self._base_dir / storage_key

    def exists(self, storage_key: str) -> bool:
        """Check whether a stored file exists."""
        return (self._base_dir / storage_key).exists()

    def delete(self, storage_key: str) -> None:
        """Delete a stored file. Silently ignores if not found."""
        path = self._base_dir / storage_key
        if path.exists():
            path.unlink()

    def get_absolute_path(self, storage_key: str) -> str:
        """Returns the absolute path as a string (for FileResponse, etc.)."""
        return str(self._base_dir / storage_key)


# Singleton — import and use this throughout the app
storage_service = StorageService()
