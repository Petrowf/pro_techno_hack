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
    start_time: str
    end_time: str
    address_ids: List[int]  # Список ID адресов, связанных с Abort

    class Config:
        from_attributes = True

from pydantic import BaseModel

class AddressSchema(BaseModel):
    id: int
    district: str
    street: str
    house: str

    class Config:
        from_attributes = True  # Для совместимости с ORM