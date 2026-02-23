import fastapi
from fastapi_chameleon import template
from app.services import data_service

router = fastapi.APIRouter()


@router.get('/')
@template(template_file='home/index.pt')
def index():
    return {
        'rooms': data_service.get_rooms()
    }


@router.post('/set_temp/{room_id}')
def set_temp(room_id: str, setpoint: float = fastapi.Form(...)):
    data_service.update_room_setpoint(room_id, setpoint)
    return fastapi.responses.RedirectResponse(url='/', status_code=303)