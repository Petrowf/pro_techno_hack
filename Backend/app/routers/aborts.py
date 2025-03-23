from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import selectinload
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession 
from app.schemas.aborts import AbortResponseSchema, AddressSchema
from app.models.users import User,UserAddress
from app.models.aborts import Abort, AbortAddress, Address
from app.database.session import get_db
from app.core.security import get_current_user
from app.services.scheduler import NotificationService
router = APIRouter()


@router.get("/user-events", response_model=List[AbortResponseSchema])
async def get_user_aborts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. Получаем все адреса пользователя
        user_address_query = select(UserAddress.address_id).where(
            UserAddress.user_id == current_user.id
        )
        user_addresses = await db.execute(user_address_query)
        address_ids = user_addresses.scalars().all()

        if not address_ids:
            return []

        # 2. Ищем связанные события
        abort_query = (
            select(Abort)
            .join(Abort.abort_addresses)
            .where(AbortAddress.address_id.in_(address_ids))
            .options(
                selectinload(Abort.abort_addresses)
                .joinedload(AbortAddress.address)
            )
            .distinct(Abort.id)  # Уникальные события по ID
            .order_by(Abort.id, Abort.start_time.desc())
        )

        result = await db.execute(abort_query)
        aborts = result.scalars().all()

        # 3. Формируем ответ
        return [
            AbortResponseSchema(
                id=abort.id,
                type=abort.type,
                reason=abort.reason,
                comment=abort.comment,
                start_time=abort.start_time,
                end_time=abort.end_time,
                address_ids=list({addr.address_id for addr in abort.abort_addresses})
            )
            for abort in aborts
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении событий: {str(e)}"
        )
    
@router.get("/addresses/{address_id}", response_model=AddressSchema)
async def get_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    
):
    
    # Используем функцию get_address_by_id для получения адреса
    address = await get_address_by_id(address_id, db)
    return address

async def get_address_by_id(
    address_id: int,
    db: AsyncSession
) -> Address:
    
    # Выполняем запрос к базе данных
    result = await db.execute(select(Address).where(Address.id == address_id))
    address = result.scalars().first()

    # Если адрес не найден, выбрасываем исключение
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Address with id {address_id} not found"
        )

    return address

async def send_abort_notifications(db: AsyncSession, abort_id: int):
    notification_service = NotificationService()
    # ... (логика получения пользователей и отправки)