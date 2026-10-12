from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, dashboard, library, audits, chat, compare, compliance, export
import os

from app.core.database import init_db_indexes
from app.core.logging import logger

app = FastAPI(title="Auditor AI Backend")

@app.on_event("startup")
async def on_startup():
    logger.info("Starting up Auditor AI Backend...")
    await init_db_indexes()


# 1. Expanded Origins — localhost for dev + production URL from env
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "")  # Set this on Render to your frontend URL
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
if CORS_ORIGIN:
    origins.append(CORS_ORIGIN)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 3. Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(library.router, prefix="/api", tags=["library"])
app.include_router(audits.router, prefix="/api", tags=["audits"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(compare.router, prefix="/api", tags=["compare"])
app.include_router(compliance.router, prefix="/api", tags=["compliance"])
app.include_router(export.router, prefix="/api", tags=["export"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Auditor AI Backend API"}
