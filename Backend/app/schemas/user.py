from pydantic import BaseModel
from typing import List, Optional

from app.schemas.aborts import AddressSchema


class UserAddressResponse(BaseModel):
    id: int
    name: str
    address: AddressSchema  

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    user_addresses: list[UserAddressResponse]  

    class Config:
        from_attributes = True

class UserAddressCreate(BaseModel):
    name: str  
    district: str
    street: str
    house: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    fcm_token: Optional[str] = None
    user_addresses: Optional[List[UserAddressCreate]] = None  

class UserAddressUpdate(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None
    street: Optional[str] = None
    house: Optional[str] = None

class UserAddressCreate(BaseModel):
    name: str
    district: str
    street: str
    house: str
