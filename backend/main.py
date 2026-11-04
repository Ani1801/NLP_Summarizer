from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
    for o in CORS_ORIGIN.split(","):
        cleaned = o.strip().rstrip("/")
        if cleaned and cleaned not in origins:
            origins.append(cleaned)

# 2. CORS Middleware (supports explicit origins + any vercel preview/prod subdomain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Server Error: {str(exc)}"},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to Auditor AI Backend API"}

@app.get("/api/health")
async def health_check():
    from app.core.database import get_database
    try:
        db = get_database()
        await db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": f"MongoDB connection failed: {str(e)}"}
