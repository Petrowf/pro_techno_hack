from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Схема для создания события
class AddressSchema(BaseModel):
    id: int
    district: str
    street: str
    house: str

    class Config:
        from_attributes = True

class AbortResponseSchema(BaseModel):
    id: int
    type: str
    reason: str
    comment: str
    start_time: datetime
    end_time: datetime
    address_ids: List[int]

    class Config:
        from_attributes = True

from pydantic import BaseModel

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

class AddressSchema(BaseModel):
    id: int
    district: str
    street: str
    house: str

    class Config:
        from_attributes = True  # Для совместимости с ORM