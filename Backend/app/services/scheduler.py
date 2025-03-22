import asyncio
import logging
from datetime import datetime, time, timedelta
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.services.notification_service import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationScheduler:
    def __init__(self):
        self.is_running = False
        self.background_tasks = BackgroundTasks()
    
    async def start(self):
        """Запускает планировщик уведомлений"""
        if self.is_running:
            return
        
        self.is_running = True
        asyncio.create_task(self._schedule_daily_notifications())
        logger.info("Notification scheduler started")
    
    async def _schedule_daily_notifications(self):
        """Планирует ежедневную отправку уведомлений"""
        while self.is_running:
            try:
                # Получаем текущее время
                now = datetime.now()
                
                # Устанавливаем время для отправки уведомлений (например, 10:00)
                target_time = time(10, 0)
                
                # Вычисляем, сколько секунд осталось до целевого времени
                target_datetime = datetime.combine(now.date(), target_time)
                if now.time() > target_time:
                    # Если текущее время уже после целевого, планируем на следующий день
                    target_datetime = datetime.combine(now.date() + timedelta(days=1), target_time)
                
                seconds_until_target = (target_datetime - now).total_seconds()
                logger.info(f"Scheduled next notification check in {seconds_until_target:.2f} seconds")
                
                # Ждем до целевого времени
                await asyncio.sleep(seconds_until_target)
                
                # Получаем новую сессию БД и отправляем уведомления
                async for db in get_db():
                    notification_service = NotificationService(db)
                    await notification_service.send_day_before_notifications(self.background_tasks)
                    break  # Используем только одну сессию
                
                logger.info("Daily notifications check completed")
                
                # Ждем 24 часа до следующей проверки
                await asyncio.sleep(24 * 60 * 60)
            
            except Exception as e:
                logger.error(f"Error in notification scheduler: {str(e)}")
                # В случае ошибки ждем 1 час и пробуем снова
                await asyncio.sleep(3600)
    
    def stop(self):
        """Останавливает планировщик"""
        self.is_running = False
        logger.info("Notification scheduler stopped")
