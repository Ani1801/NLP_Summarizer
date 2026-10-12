from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserLogin, Token, GoogleToken, ProfileUpdate, PasswordUpdate, UserResponse
from app.services.auth_service import AuthService
from app.services.google_auth_service import GoogleAuthService
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db = Depends(get_db)):
    return await AuthService.signup(user, db)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db = Depends(get_db)):
    return await AuthService.login(user_credentials, db)

@router.post("/google", response_model=Token)
async def google_login(payload: GoogleToken, db = Depends(get_db)):
    """
    Google Identity Services authentication endpoint.
    Accepts a Google ID token credential, verifies it server-side,
    then resolves or creates the application user and returns the
    application's standard JWT session — identical to email/password login.
    """
    return await GoogleAuthService.google_login(payload.credential, db)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        role=current_user.get("role", "Researcher"),
        created_at=current_user.get("created_at")
    )

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    return await AuthService.update_profile(current_user, profile_data, db)

@router.put("/password")
async def update_password(
    password_data: PasswordUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    return await AuthService.update_password(current_user, password_data, db)
