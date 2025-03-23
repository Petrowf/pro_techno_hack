from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.models.aborts import Address
from app.models.users import User, UserAddress

from app.schemas.user import UserAddressUpdate, UserAddressCreate, UserUpdate


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
        try:
            # Получаем пользователя с адресами и связанными Address
            result = await self.db.execute(
                select(User)
                .options(
                    selectinload(User.user_addresses)
                    .joinedload(UserAddress.address)  # Загружаем связанные Address
                )
                .where(User.id == user_id)
            )
            user = result.scalars().first()

            if not user:
                raise ValueError("User not found")

            # Обновляем основные данные
            if user_data.name:
                user.name = user_data.name
            if user_data.phone:
                user.phone = user_data.phone
            if user_data.fcm_token:
                user.fcm_token = user_data.fcm_token

            # Обрабатываем адреса только если они переданы
            if user_data.user_addresses:
                # Получаем существующие адреса пользователя
                existing_addresses = {
                    (ua.address.district, ua.address.street, ua.address.house)
                    for ua in user.user_addresses
                }

                for addr in user_data.user_addresses:
                    # Проверяем, не существует ли уже такой адрес у пользователя
                    if (addr.district, addr.street, addr.house) in existing_addresses:
                        continue

                    # Проверяем существование адреса в базе
                    address_result = await self.db.execute(
                        select(Address).where(
                            Address.district == addr.district,
                            Address.street == addr.street,
                            Address.house == addr.house
                        )
                    )
                    address = address_result.scalars().first()

                    # Создаем новый адрес если не существует
                    if not address:
                        address = Address(
                            district=addr.district,
                            street=addr.street,
                            house=addr.house
                        )
                        self.db.add(address)
                        await self.db.flush()

                    # Создаем новую связь UserAddress
                    user_address = UserAddress(
                        user_id=user_id,
                        address_id=address.id,
                        name=addr.name
                    )
                    user.user_addresses.append(user_address)  # Добавляем к существующим

            await self.db.commit()
            await self.db.refresh(user, ["user_addresses"])
            return user

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise RuntimeError(f"Database error: {str(e)}")
        
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

    async def update_user_address(
    self, 
    address_id: int,  # Должен быть integer
    address_data: UserAddressUpdate,
    current_user: User
) -> User:
        try:
            result = await self.db.execute(
                select(UserAddress)
                .where(
                    UserAddress.id == address_id,  # Используем числовой ID
                    UserAddress.user_id == current_user.id
                )
                .options(joinedload(UserAddress.address))
            )
            user_address = result.scalars().first()

            if not user_address:
                raise ValueError("Address not found")

            # Обновление названия
            if address_data.name is not None:
                user_address.name = address_data.name

            # Обновление физического адреса
            if any([address_data.district, address_data.street, address_data.house]):
                new_district = address_data.district or user_address.address.district
                new_street = address_data.street or user_address.address.street
                new_house = address_data.house or user_address.address.house

                # Исправлено: добавлен await перед execute
                address_result = await self.db.execute(
                    select(Address).where(
                        Address.district == new_district,
                        Address.street == new_street,
                        Address.house == new_house
                    )
                )
                new_address = address_result.scalars().first()

                if not new_address:
                    new_address = Address(
                        district=new_district,
                        street=new_street,
                        house=new_house
                    )
                    self.db.add(new_address)
                    await self.db.flush()

                user_address.address_id = new_address.id

            await self.db.commit()
            return await self.get_user(current_user.id)

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise RuntimeError(f"Database error: {str(e)}")
        


    
    async def add_user_address(
        self,
        address_data: UserAddressCreate,
        current_user: User
    ) -> User:
        """Добавление нового адреса текущему пользователю"""
        try:
            # Проверка существования адреса
            address_result = await self.db.execute(
                select(Address)
                .where(
                    Address.district == address_data.district,
                    Address.street == address_data.street,
                    Address.house == address_data.house
                ))
            address = address_result.scalars().first()

            # Создаем новый адрес если не существует
            if not address:
                address = Address(
                    district=address_data.district,
                    street=address_data.street,
                    house=address_data.house
                )
                self.db.add(address)
                await self.db.flush()

            # Проверка существующей связи
            existing_link = await self.db.execute(
                select(UserAddress)
                .where(
                    UserAddress.user_id == current_user.id,
                    UserAddress.address_id == address.id
                ))
            if existing_link.scalars().first():
                raise HTTPException(
                    status_code=400,
                    detail="Address already linked to your account"
                )

            # Создаем новую связь
            new_user_address = UserAddress(
                user_id=current_user.id,
                address_id=address.id,
                name=address_data.name
            )
            self.db.add(new_user_address)
            await self.db.commit()

            return await self.get_user(current_user.id)

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

    async def get_user(self, user_id: int) -> User:
        """Получение пользователя с полной информацией об адресах"""
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.user_addresses)
                .joinedload(UserAddress.address)
            )
            .where(User.id == user_id)
        )
        return result.scalars().first()