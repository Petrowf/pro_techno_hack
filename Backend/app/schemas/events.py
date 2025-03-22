from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    address: str

class AbortCreate(BaseModel):
    type: str
    reason: str
    comment: str | None = None
    start_time: datetime
    end_time: datetime | None = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class EventResponse(BaseModel):
    id: int
    type: str
    reason: str
    start_time: datetime
    end_time: datetime

    class Config:
        orm_mode = True

        
class SubscriptionCreate(BaseModel):
    address: str

class SubscriptionResponse(BaseModel):
    id: int
    address: str
    
    class Config:
        from_attributes = True

class FCMTokenUpdate(BaseModel):
    fcm_token: str
