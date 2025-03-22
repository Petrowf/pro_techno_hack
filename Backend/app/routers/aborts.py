from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession 
from app.schemas.aborts import AbortCreateSchema, AbortResponseSchema
from app.models.users import User,UserAddress
from app.models.aborts import Abort, AbortAddress, Address
from app.database.session import get_db
from app.core.security import get_current_user
from app.services.scheduler import NotificationService
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_abort(
    abort_data: AbortCreateSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_abort = Abort(**abort_data.dict(exclude={"address_ids"}))
        db.add(new_abort)
        db.commit()

        # Привязка адресов
        for address_id in abort_data.address_ids:
            if not db.query(Address).get(address_id):
                db.rollback()
                raise HTTPException(
                    status_code=404,
                    detail=f"Address {address_id} not found"
                )
            db.add(AbortAddress(
                abort_id=new_abort.id,
                address_id=address_id
            ))
        
        db.commit()

        # Фоновая задача для уведомлений
        background_tasks.add_task(
            send_abort_notifications,
            db=db,
            abort_id=new_abort.id
        )

        return {"id": new_abort.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-events", response_model=List[AbortResponseSchema])
async def get_user_aborts(
    db: AsyncSession = Depends(get_db),  # Используем асинхронную сессию
    current_user: User = Depends(get_current_user)
):
    try:
        # Получаем все адреса пользователя
        user_addresses = (await db.execute(
            select(UserAddress.address_id)
            .where(UserAddress.user_id == current_user.id)
        )).scalars().all()

        # Получаем ID связанных событий
        abort_ids = (await db.execute(
            select(AbortAddress.abort_id)
            .where(AbortAddress.address_id.in_(user_addresses))
        )).scalars().all()

        # Получаем полные данные событий
        aborts = (await db.execute(
            select(Abort)
            .where(Abort.id.in_(abort_ids))
        )).scalars().all()

        return aborts

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
async def send_abort_notifications(db: AsyncSession, abort_id: int):
    notification_service = NotificationService()
    # ... (логика получения пользователей и отправки)