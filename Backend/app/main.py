from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import auth, users, aborts
from app.database import base, session
from app.core.config import settings
from app.services.scheduler import event_listener

app = FastAPI(
    title="Auth",
    version="0.1.0"  ,
    docs_url="/docs" if settings.ENVIRONMENT == "dev" else None
)


import asyncio

# Создаем менеджер жизненного цикла
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код при запуске
    task = asyncio.create_task(event_listener.start())
    print("✅ Слушатель событий PostgreSQL запущен")
    
    yield  # Здесь приложение работает
    
    # Код при завершении
    await event_listener.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("❌ Слушатель событий остановлен")



# Подключение роутеров
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(aborts.router, prefix=settings.API_V1_STR)



@app.get("/health")
async def health_check():
    return {"status": "ok"}
