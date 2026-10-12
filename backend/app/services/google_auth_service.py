"""
google_auth_service.py — Google Identity Services authentication for DocSummarizer.

Flow:
  1. Frontend sends Google ID token (credential) from Google's one-tap / button.
  2. Backend verifies the token cryptographically using google-auth library.
  3. Extracts verified claims: sub, email, name, picture.
  4. Resolves/creates/links application user in the existing users collection.
  5. Issues the application's own JWT (same structure as email/password login).
  6. Returns the identical Token response structure the frontend already expects.

Account resolution cases:
  Case A — New user: create fresh user document, google_sub set, password_hash=None.
  Case B — Existing google_sub match: log in directly.
  Case C — Existing local account with same email: link google_sub, log in with existing _id.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.core.security import create_access_token
from app.core.logging import logger
from app.schemas.user import Token


import os

def _verify_google_token(credential: str) -> dict:
    """
    Cryptographically verify the Google ID token.
    Returns the verified claims dict or raises HTTPException.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID") or settings.GOOGLE_CLIENT_ID
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication is not configured on this server.",
        )

    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id,
        )
    except ValueError as exc:
        logger.warning(f"Google token verification failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google credential. Please try again.",
        )

    # Validate required claims are present
    required_claims = ("sub", "email", "email_verified")
    for claim in required_claims:
        if claim not in id_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google credential is missing required identity information.",
            )

    if not id_info.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email is not verified. Please verify your Google account first.",
        )

    return id_info


def _build_token_response(user_doc: dict) -> Token:
    """Build the standard application Token response from a users collection document."""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_doc["email"]},
        expires_delta=expires_delta,
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user_doc["_id"]),
            "name": user_doc["name"],
            "email": user_doc["email"],
            "role": user_doc.get("role", "Researcher"),
            "created_at": user_doc.get("created_at"),
        },
    )


class GoogleAuthService:
    @staticmethod
    async def google_login(credential: str, db) -> Token:
        """
        Verify the Google ID token and resolve/create the application user.
        Returns the same Token structure as email/password login.
        """
        # Step 1 — Verify token cryptographically (raises if invalid)
        id_info = _verify_google_token(credential)

        google_sub: str = id_info["sub"]
        google_email: str = id_info["email"]
        google_name: str = id_info.get("name", google_email.split("@")[0])
        google_picture: Optional[str] = id_info.get("picture")

        users_col = db["users"]
        now = datetime.utcnow()

        # Step 2 — Case B: Existing user with this google_sub
        user = await users_col.find_one({"google_sub": google_sub})
        if user:
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated.",
                )
            # Update last_login timestamp
            await users_col.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login_at": now, "updated_at": now}},
            )
            logger.info(f"Google login — existing google_sub user: {google_email}")
            return _build_token_response(user)

        # Step 3 — Case C: Existing local account with same verified email → link Google
        user = await users_col.find_one({"email": google_email})
        if user:
            if not user.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account has been deactivated.",
                )
            # Link the google_sub to the existing local account
            update_fields = {
                "google_sub": google_sub,
                "last_login_at": now,
                "updated_at": now,
                "auth_providers.google": True,
            }
            # Only set profile picture if the user doesn't already have one
            if google_picture and not user.get("profile_picture"):
                update_fields["profile_picture"] = google_picture
            await users_col.update_one(
                {"_id": user["_id"]},
                {"$set": update_fields},
            )
            logger.info(f"Google login — linked Google to existing local account: {google_email}")
            # Return updated doc
            user = await users_col.find_one({"_id": user["_id"]})
            return _build_token_response(user)

        # Step 4 — Case A: Brand new user — create application account
        user_id = str(uuid.uuid4())
        new_user = {
            "_id": user_id,
            "name": google_name,
            "email": google_email,
            "password_hash": None,           # No password for Google-only users
            "google_sub": google_sub,
            "profile_picture": google_picture,
            "role": "Researcher",            # Default role
            "auth_providers": {
                "local": False,
                "google": True,
            },
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login_at": now,
        }
        await users_col.insert_one(new_user)
        logger.info(f"Google login — new user created: {google_email}")
        return _build_token_response(new_user)
