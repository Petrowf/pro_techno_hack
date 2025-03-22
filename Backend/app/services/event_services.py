from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional
from datetime import date, datetime, timedelta

from Backend.app.models.aborts import Event, UserSubscription
from app.models.users import User
from app.schemas.events import EventCreate, EventUpdate

class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_event(self, event_data: EventCreate) -> Event:
        new_event = Event(**event_data.dict())
        self.db.add(new_event)
        await self.db.commit()
        await self.db.refresh(new_event)
        return new_event
    
    async def get_event(self, event_id: int) -> Optional[Event]:
        result = await self.db.execute(select(Event).where(Event.id == event_id))
        return result.scalars().first()
    
    async def update_event(self, event_id: int, event_data: EventUpdate) -> Optional[Event]:
        update_data = event_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.db.execute(
                update(Event)
                .where(Event.id == event_id)
                .values(**update_data)
            )
            await self.db.commit()
        
        return await self.get_event(event_id)
    
    async def delete_event(self, event_id: int) -> bool:
        await self.db.execute(delete(Event).where(Event.id == event_id))
        await self.db.commit()
        return True
    
    async def get_events_by_date(self, target_date: date) -> List[Event]:
        result = await self.db.execute(
            select(Event)
            .where(Event.event_date == target_date, Event.is_active == True)
        )
        return result.scalars().all()
    
    async def get_tomorrow_events(self) -> List[Event]:
        tomorrow = datetime.now().date() + timedelta(days=1)
        return await self.get_events_by_date(tomorrow)
    
    async def create_subscription(self, user_id: int, address: str) -> UserSubscription:
        # Проверяем, существует ли уже подписка
        result = await self.db.execute(
            select(UserSubscription)
            .where(
                UserSubscription.user_id == user_id,
                UserSubscription.address == address
            )
        )
        existing = result.scalars().first()
        
        if existing:
            return existing
        
        # Создаем новую подписку
        new_subscription = UserSubscription(user_id=user_id, address=address)
        self.db.add(new_subscription)
        await self.db.commit()
        await self.db.refresh(new_subscription)
        return new_subscription
    
    async def get_users_by_address(self, address: str) -> List[User]:
        result = await self.db.execute(
            select(User)
            .join(UserSubscription)
            .where(UserSubscription.address == address)
        )
        return result.scalars().all()
