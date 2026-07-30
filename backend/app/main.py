"""
main.py (app)
--------------
FastAPI application factory. Wires up CORS, all routers, and runs startup
tasks: creating the SQLite database schema (if not present) and seeding a
default admin account so the admin dashboard is usable immediately.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import User, UserRole
from app.routers import admin, analytics, auth, chat, feedback, history
from app.security import hash_password
from app.utils.logger import logger


def seed_default_admin() -> None:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL).first()
        if not existing:
            admin_user = User(
                name=settings.DEFAULT_ADMIN_NAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
            )
            db.add(admin_user)
            db.commit()
            logger.info(
                f"Seeded default admin account -> email={settings.DEFAULT_ADMIN_EMAIL} "
                f"password={settings.DEFAULT_ADMIN_PASSWORD}"
            )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} ...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema ensured (tables created if not present).")
    seed_default_admin()
    yield
    logger.info("Shutting down application.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Based Customer Support Auto-Responder using LLMs, RAG, intent "
        "classification, and sentiment analysis for automated query handling."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(feedback.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "docs": "/docs",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
