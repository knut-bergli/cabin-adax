import fastapi
from fastapi_chameleon import template
from app.services import data_service
from app.models.db_session import db_dependency

router = fastapi.APIRouter()


@router.get('/')
@template(template_file='home/index.pt')
async def index(db: db_dependency):
    rooms = await data_service.get_rooms(db)
    return {
        'rooms': rooms
    }


@router.post('/set_temp/{room_id}')
async def set_temp(room_id: str, setpoint: float = fastapi.Form(...), db: db_dependency = None):
    await data_service.update_room_setpoint(db, room_id, setpoint)
    return fastapi.responses.RedirectResponse(url='/', status_code=303)