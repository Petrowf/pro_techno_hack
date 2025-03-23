from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

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


