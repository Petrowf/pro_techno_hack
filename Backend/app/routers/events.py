from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.users import User, UserAddress
from app.models.aborts import Abort, AbortAddress
from app.core.security import get_current_user

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/my")
async def get_user_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Получить все адреса пользователя
    user_addresses = db.query(UserAddress.address_id).filter(
        UserAddress.user_id == current_user.id
    ).all()

    # Найти связанные события
    abort_ids = db.query(AbortAddress.abort_id).filter(
        AbortAddress.address_id.in_([addr.address_id for addr in user_addresses])
    ).all()

    # Получить детали событий
    events = db.query(Abort).filter(Abort.id.in_([abort.abort_id for abort in abort_ids])).all()

    return {"events": events}