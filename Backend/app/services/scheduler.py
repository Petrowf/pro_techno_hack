import asyncpg
import asyncio
from app.core.config import settings
from app.services.notification_service import notification_service

class EventListener:
    def __init__(self):
        self.connection = None
        self.is_running = False

    async def start(self):
        self.is_running = True
        while self.is_running:
            try:
                self.connection = await asyncpg.connect(settings.DATABASE_URL)
                await self.connection.add_listener('new_aborts', self.handle_event)
                print("🚀 Слушатель событий PostgreSQL запущен")
                while True:
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"Ошибка подключения: {str(e)}")
                await asyncio.sleep(5)

    async def handle_event(self, connection, pid, channel, payload):
        print(f"Получено событие: {payload}")
        await notification_service.send_to_matching_users(int(payload))

    async def stop(self):
        self.is_running = False
        if self.connection:
            await self.connection.close()

event_listener = EventListener()