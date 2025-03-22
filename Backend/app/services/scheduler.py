import asyncio
from threading import Thread
import asyncpg
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.services.notification_service import NotificationService
from app.models.aborts import Abort, AbortAddress
from app.models.users import User, UserAddress
import logging

# Импортируем существующие настройки подключения
from app.database.session import get_db  # Убедитесь в правильном пути импорта

logger = logging.getLogger(__name__)

class EventWatcher:
    def __init__(self):
        self.notification_service = NotificationService(
            project_id=settings.FCM_PROJECT_ID,
            service_account_file=settings.FCM_SERVICE_ACCOUNT
        )
        self._start_listener()

    def _start_listener(self):
        Thread(target=self._listen_db, daemon=True).start()

    def _listen_db(self):
        try:
            asyncio.run(self._async_listen_db())
        except Exception as e:
            logger.error(f"Ошибка в слушателе базы данных: {str(e)}")

    async def _async_listen_db(self):
        try:
            # Подключение к PostgreSQL через asyncpg
            conn = await asyncpg.connect(
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT
            )
            logger.info("Слушатель базы данных запущен.")
            await conn.add_listener("new_abort", self._process_notification)
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {str(e)}")

    async def _process_notification(self, connection, pid, channel, payload):
        try:
            abort_id = int(payload)
            await self._process_abort(abort_id)
        except Exception as e:
            logger.error(f"Ошибка обработки уведомления: {str(e)}")

    async def _process_abort(self, abort_id: int):
        async with get_db() as db:
            try:
                abort = await db.get(Abort, abort_id)
                if not abort:
                    return

                addresses = (await db.execute(
                    select(AbortAddress.address_id)
                    .where(AbortAddress.abort_id == abort_id)
                )).scalars().all()

                users = (await db.execute(
                    select(User)
                    .join(UserAddress)
                    .where(UserAddress.address_id.in_(addresses))
                )).scalars().all()

                valid_tokens = [u.fcm_token for u in users if u.fcm_token]
                
                await self.notification_service.send_notification(
                    fcm_tokens=valid_tokens,
                    title="Новое отключение",
                    message=f"{abort.type}: {abort.reason}",
                    data={"event_id": abort_id}
                )

            except Exception as e:
                logger.error(f"Ошибка обработки события: {str(e)}")
                await db.rollback()
            finally:
                await db.close()

event_listener = EventWatcher()