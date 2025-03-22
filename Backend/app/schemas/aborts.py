from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Схема для создания события
class AbortCreateSchema(BaseModel):
    type: str = Field(..., description="Тип события")
    reason: str = Field(..., description="Причина события")
    comment: Optional[str] = Field(None, description="Комментарий к событию")
    start_time: datetime = Field(..., description="Время начала события")
    end_time: datetime = Field(..., description="Время окончания события")
    address_ids: List[int] = Field(..., description="Список ID адресов, связанных с событием")

# Схема для ответа с данными о событии
class AbortResponseSchema(BaseModel):
    id: int = Field(..., description="ID события")
    type: str = Field(..., description="Тип события")
    reason: str = Field(..., description="Причина события")
    comment: Optional[str] = Field(None, description="Комментарий к событию")
    start_time: datetime = Field(..., description="Время начала события")
    end_time: datetime = Field(..., description="Время окончания события")
    address_ids: List[int] = Field(..., description="Список ID адресов, связанных с событием")

    class Config:
        orm_mode = True  # Для корректной работы с ORM моделями