from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import logging

from app.models.aborts import Abort, Address, AbortAddress
from app.models.users import User, UserAddress

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def notify_on_abort_update(self, abort_id: int, background_tasks: BackgroundTasks):
        """Отправляет уведомления при обновлении события (аборта)"""
        # Получаем обновленное событие
        result = await self.db.execute(select(Abort).where(Abort.id == abort_id))
        abort = result.scalars().first()
        
        if not abort:
            logger.warning(f"Событие с ID {abort_id} не найдено")
            return
        
        # Получаем адреса, связанные с этим событием
        result = await self.db.execute(
            select(Address)
            .join(AbortAddress)
            .where(AbortAddress.abort_id == abort_id)
        )
        addresses = result.scalars().all()
        
        # Для каждого адреса находим пользователей, которые подписаны на него
        for address in addresses:
            result = await self.db.execute(
                select(User)
                .join(UserAddress)
                .where(UserAddress.address_id == address.id)
            )
            users = result.scalars().all()
            
            # Отправляем уведомления пользователям
            for user in users:
                if user.fcm_token:
                    background_tasks.add_task(
                        self._send_fcm_notification,
                        user.fcm_token,
                        "Обновление события",
                        f"Событие по адресу {address.district}, {address.street}, {address.house} было обновлено"
                    )
    
    async def send_day_before_notifications(self, background_tasks: BackgroundTasks):
        """Отправляет уведомления за день до события"""
        tomorrow = datetime.now() + timedelta(days=1)
        
        # Находим события, которые начинаются завтра
        result = await self.db.execute(
            select(Abort).where(
                and_(
                    Abort.start_time >= tomorrow.replace(hour=0, minute=0, second=0, microsecond=0),
                    Abort.start_time < tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
                )
            )
        )
        aborts = result.scalars().all()
        
        for abort in aborts:
            # Получаем адреса, связанные с этим событием
            result = await self.db.execute(
                select(Address)
                .join(AbortAddress)
                .where(AbortAddress.abort_id == abort.id)
            )
            addresses = result.scalars().all()
            
            # Для каждого адреса находим пользователей, которые подписаны на него
            for address in addresses:
                result = await self.db.execute(
                    select(User)
                    .join(UserAddress)
                    .where(UserAddress.address_id == address.id)
                )
                users = result.scalars().all()
                
                # Отправляем уведомления пользователям
                for user in users:
                    if user.fcm_token:
                        background_tasks.add_task(
                            self._send_fcm_notification,
                            user.fcm_token,
                            "Напоминание о событии",
                            f"Завтра состоится событие по адресу {address.district}, {address.street}, {address.house}"
                        )
    
    async def _send_fcm_notification(self, token: str, title: str, body: str):
        """
        Отправляет уведомление через Firebase Cloud Messaging
        В реальной реализации здесь будет код для отправки через FCM API
        """
        try:
            # Здесь должен быть код для отправки через Firebase Admin SDK
            # Для примера просто логируем
            logger.info(f"FCM notification sent: title='{title}', body='{body}', token='{token}'")
            
            # В реальной реализации:
            # from firebase_admin import messaging
            # message = messaging.Message(
            #     notification=messaging.Notification(title=title, body=body),
            #     token=token,
            # )
            # response = messaging.send(message)
            # return {"success": True, "message_id": response}
            
            return {"success": True, "message": "Notification sent (mock)"}
        
        except Exception as e:
            logger.error(f"Error sending FCM notification: {str(e)}")
            return {"success": False, "error": str(e)}
