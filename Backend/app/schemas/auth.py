from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.models.users import User

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    name: str | None = None

class UserAuth(BaseModel):
    login: str
    password: str

class UserCreate(BaseModel):
    login: str
    password: str
    name: str

class AddressCreate(BaseModel):
    district: str
    street: str
    house: str



class AddressResponse(BaseModel):
    id: int
    district: str
    street: str
    house: str

    class Config:
        from_attributes = True

        
class UserAddressResponse(BaseModel):
    id: int
    name: str
    address: AddressResponse  # Вложенный адрес

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    user_addresses: list[UserAddressResponse]  # Используем новую схему

    class Config:
        from_attributes = True

class UserAddressCreate(BaseModel):
    name: str  # Название адреса (например "Дом" или "Офис")
    district: str
    street: str
    house: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    fcm_token: Optional[str] = None
    user_addresses: Optional[List[UserAddressCreate]] = None  # Список адресов для добавления

class FCMTokenUpdate(BaseModel):
    fcm_token: str



class LoginRequest(BaseModel):
    login: str
    password: str
