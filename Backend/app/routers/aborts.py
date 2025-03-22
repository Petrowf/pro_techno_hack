from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.session import get_db
from app.models.users import User
from app.services.notification_service import NotificationService
from app.core.security import get_current_user

router = APIRouter(tags=["Aborts"])

@router.post("/update-fcm-token", status_code=status.HTTP_200_OK)
async def update_fcm_token(
    fcm_token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление FCM токена пользователя"""
    current_user.fcm_token = fcm_token
    db.add(current_user)
    await db.commit()
    return {"message": "FCM токен успешно обновлен"}

@router.post("/notify-on-update/{abort_id}", status_code=status.HTTP_200_OK)
async def notify_on_abort_update(
    abort_id: int, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправляет уведомления при обновлении события"""
    notification_service = NotificationService(db)
    await notification_service.notify_on_abort_update(abort_id, background_tasks)
    return {"message": "Уведомления отправлены"}
