from fastapi import APIRouter, Depends
#from app.services.event_services import EventService
from app.schemas.events import AbortCreate

router = APIRouter()
"""""
@router.post("/aborts")
async def create_abort(

    abort_data: AbortCreate, 
    address_ids: list[int],
    service: EventService = Depends()
):
    return await service.create_abort_with_notification(abort_data.dict(), address_ids)"
    """