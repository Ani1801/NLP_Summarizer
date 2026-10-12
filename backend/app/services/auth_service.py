import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.schemas.user import UserCreate, UserLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token, validate_password_strength
from app.core.config import settings

class AuthService:
    @staticmethod
    async def signup(user: UserCreate, db) -> Token:
        users_collection = db["users"]
        
        # 1. Validate password strength
        if not validate_password_strength(user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long."
            )
        
        # 2. Check existing user
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 3. Hash password and insert
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user.password)
        now = datetime.utcnow()
        
        new_user = {
            "_id": user_id,
            "name": user.name,
            "email": user.email,
            "password_hash": hashed_password,
            "role": user.role,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "last_login_at": now
        }
        
        await users_collection.insert_one(new_user)
        
        # 4. Generate JWT
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=expires_delta
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": now
            }
        )

    @staticmethod
    async def login(user_credentials: UserLogin, db) -> Token:
        users_collection = db["users"]
        
        user = await users_collection.find_one({"email": user_credentials.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account does not exist. Please create an account."
            )
            
        if not verify_password(user_credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        # Update last login timestamp
        now = datetime.utcnow()
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login_at": now}}
        )
            
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=expires_delta
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "created_at": user.get("created_at")
            }
        )

    @staticmethod
    async def update_profile(current_user: dict, profile_data, db) -> dict:
        users_collection = db["users"]
        update_fields = {"updated_at": datetime.utcnow()}
        if profile_data.name:
            update_fields["name"] = profile_data.name
        if profile_data.role:
            update_fields["role"] = profile_data.role
        
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_fields}
        )
        updated_user = await users_collection.find_one({"_id": current_user["_id"]})
        return {
            "id": str(updated_user["_id"]),
            "name": updated_user["name"],
            "email": updated_user["email"],
            "role": updated_user.get("role", "Researcher"),
            "created_at": updated_user.get("created_at")
        }

    @staticmethod
    async def update_password(current_user: dict, password_data, db):
        users_collection = db["users"]
        user = await users_collection.find_one({"_id": current_user["_id"]})
        
        if not user.get("password_hash"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google authenticated accounts do not have a password set."
            )
            
        if not verify_password(password_data.current_password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect."
            )
            
        new_hash = get_password_hash(password_data.new_password)
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"password_hash": new_hash, "updated_at": datetime.utcnow()}}
        )
        return {"message": "Password updated successfully."}
