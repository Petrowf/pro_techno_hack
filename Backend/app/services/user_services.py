from requests import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User, UserAddress
from app.models.aborts import Address
from app.schemas.auth import UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, login: str, password: str) -> User | None:
        result = await self.db.execute(select(User).where(User.login == login))
        user = result.scalars().first()
        print(user)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, login: str, password: str, name: str) -> User:
        # Проверка уникальности логина
        existing_user = await self.db.execute(
            select(User).where(User.login == login))
        if existing_user.scalars().first():
            raise ValueError("Login already exists")
        
        new_user = User(
            login=login,
            hashed_password=get_password_hash(password),
            name=name
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        # Обновляем основные данные пользователя
        user = await self.db.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        for key, value in user_data.dict(exclude={"address_ids"}).items():
            if value is not None:
                setattr(user, key, value)

        # Обновляем адреса, если они переданы
        if user_data.address_ids is not None:
            # Удаляем старые связи
            await self.db.execute(
                delete(UserAddress)
                .where(UserAddress.user_id == user_id)
            )
            
            # Добавляем новые адреса
            for address_id in user_data.address_ids:
                # Проверяем существование адреса
                address = await self.db.get(Address, address_id)
                if not address:
                    raise ValueError(f"Address {address_id} not found")
                
                self.db.add(UserAddress(
                    user_id=user_id,
                    address_id=address_id,
                    name=f"Address {address_id}"  # Пример, можно настроить
                ))

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int):
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise ValueError("User not found")
        
        await self.db.delete(user)
        await self.db.commit()

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()