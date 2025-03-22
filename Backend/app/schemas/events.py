from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: date
    address: str

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[date] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

class EventResponse(EventBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    address: str

class SubscriptionResponse(BaseModel):
    id: int
    address: str
    
    class Config:
        from_attributes = True

class FCMTokenUpdate(BaseModel):
    fcm_token: str
