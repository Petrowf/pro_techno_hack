from contextlib import asynccontextmanager
from fastapi import Body, FastAPI
from app.routers import auth, users, aborts
from app.database import base, session
from app.core.config import settings
from app.services.scheduler import event_listener
from firebase_admin import credentials, messaging
import firebase_admin
from app.core.config import settings
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

cred = credentials.Certificate(settings.FCM_SERVICE_ACCOUNT)
firebase_admin.initialize_app(cred)
@app.post("/send-notification")
async def send_notification(device_token: str = Body(...),  # Используем Body для получения данных из JSON
    title: str = Body(...),        # Используем Body для получения данных из JSON
    body: str = Body(...)):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=device_token,
    )
    try:
        response = messaging.send(message)
        return {"status": "success", "message_id": response}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
