from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import auth, users, aborts
from app.database import base, session
from app.core.config import settings
from app.services.scheduler import NotificationScheduler

app = FastAPI(
    title="Auth",
    version="0.1.0"  ,
    docs_url="/docs" if settings.ENVIRONMENT == "dev" else None
)

# Инициализация планировщика
scheduler = NotificationScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код выполнения при старте
    async with session.engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)
    
    # Запускаем планировщик уведомлений
    await scheduler.start()
    
    yield
    
    # Код выполнения при завершении
    scheduler.stop()
    await session.engine.dispose()

# Подключение роутеров
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(aborts.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
