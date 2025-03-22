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
        # Запрос с объединением таблиц и подгрузкой адресов
        query = (
            select(Abort)
            .join(AbortAddress, Abort.id == AbortAddress.abort_id)
            .join(UserAddress, AbortAddress.address_id == UserAddress.address_id)
            .where(UserAddress.user_id == current_user.id)
            .options(selectinload(Abort.abort_addresses))  # Подгрузка связанных адресов
        )

        result = await db.execute(query)
        aborts = result.scalars().all()

        # Преобразуем данные в схему ответа
        response = []
        for abort in aborts:
            abort_data = AbortResponseSchema(
                id=abort.id,
                type=abort.type,
                reason=abort.reason,
                comment=abort.comment,
                start_time=abort.start_time.isoformat() if abort.start_time else None,
                end_time=abort.end_time.isoformat() if abort.end_time else None,
                address_ids=[addr.address_id for addr in abort.abort_addresses]
            )
            response.append(abort_data)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/addresses/{address_id}", response_model=AddressSchema)
async def get_address(
    address_id: int,
    db: AsyncSession = Depends(get_db)
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