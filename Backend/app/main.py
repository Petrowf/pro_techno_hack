from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import auth, users
from app.database import base, session
from app.core.config import settings

app = FastAPI(
    title="Auth Service",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT == "dev" else None
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код выполнения при старте
    async with session.engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)
    yield
    # Код выполнения при завершении (опционально)
    await session.engine.dispose()
# Подключение роутеров
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok"}