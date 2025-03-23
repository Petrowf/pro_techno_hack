from fastapi import APIRouter, Body, Depends, HTTPException, status
from requests import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.aborts import UserAddressCreate, UserAddressUpdate
from app.database.session import get_db
from app.schemas.auth import UserResponse, UserUpdate
from app.services.user_services import UserService
from app.core.security import get_current_user
from app.models.users import User

router = APIRouter(tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """Получить данные текущего аутентифицированного пользователя"""
    return current_user

# routers/users.py
@router.put("/me/fcm_token")
async def update_fcm_token(
    token: str = Body(..., embed=True), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.fcm_token = token
    db.commit()
    return {"status": "ok"}

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные пользователя, включая адреса"""
    try:
        updated_user = await UserService(db).update_user(current_user.id, user_data)
        return UserResponse.from_orm(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить текущего пользователя"""
    await UserService(db).delete_user(current_user.id)
    return {"detail": "User deleted successfully"}

# Для администраторов
@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить всех пользователей (только для администраторов)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return await UserService(db).get_all_users()

@router.patch("/me/addresses/{address_id}", response_model=UserResponse)
async def update_user_address(
    address_id: int,
    address_data: UserAddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated_user = await UserService(db).update_user_address(
            address_id,        # Первый аргумент - ID адреса
            address_data,      # Второй - данные для обновления
            current_user       # Третий - пользователь
        )
        return UserResponse.from_orm(updated_user)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(500, detail=str(e))

@router.post("/me/addresses", response_model=UserResponse)
async def add_user_address(
    address_data: UserAddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated_user = await UserService(db).add_user_address(
            current_user=current_user,
            address_data=address_data
        )
        return UserResponse.from_orm(updated_user)
    except RuntimeError as e:
        raise HTTPException(500, detail=str(e))