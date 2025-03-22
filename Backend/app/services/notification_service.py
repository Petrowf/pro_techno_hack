import asyncpg
from firebase_admin import messaging
from app.core.config import settings
from app.database.session import get_db

class NotificationService:
    async def send_to_matching_users(self, abort_id: int):
        async with get_db() as db:
            # Находим пользователей с совпадающими адресами
            query = """
                SELECT DISTINCT u.fcm_token 
                FROM users_addresses ua
                JOIN aborts_addresses aa ON ua.address_id = aa.address_id
                JOIN users u ON ua.user_id = u.id
                WHERE aa.abort_id = $1
                AND u.fcm_token IS NOT NULL
            """
            result = await db.execute(query, abort_id)
            users = result.scalars().all()

            # Отправляем уведомления
            for token in users:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title="Новое событие",
                        body="В вашем районе добавлено новое событие"
                    ),
                    token=token
                )
                try:
                    messaging.send(message)
                except Exception as e:
                    print(f"Ошибка отправки: {str(e)}")

notification_service = NotificationService()