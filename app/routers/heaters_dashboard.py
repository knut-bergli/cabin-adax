from datetime import datetime
import zoneinfo
import fastapi
from fastapi_chameleon import template
from app.services import data_service
from app.models.db_session import db_dependency
from app.config.load_environment import get_settings

router = fastapi.APIRouter(
    prefix="/heaters",
    tags=["heaters"]
)


@router.get('/')
@template(template_file='heaters_dashboard/heaters_dashboard.pt')
async def index(db: db_dependency):
    rooms = await data_service.get_rooms(db, refresh_heaters=True)
    settings = get_settings()
    tz_name = getattr(settings, 'TIMEZONE', 'Europe/Oslo')
    try:
        tz = zoneinfo.ZoneInfo(tz_name)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
    last_updated = now.strftime('%H:%M:%S')
    refresh_interval = getattr(settings, 'DASHBOARD_REFRESH_INTERVAL', 120)

    return {
        'rooms': rooms,
        'last_updated': last_updated,
        'refresh_interval': refresh_interval,
    }


@router.post('/set_temp/{room_id}')
async def set_temp(room_id: int, db: db_dependency, setpoint: float = fastapi.Form(...)):
    await data_service.update_room_setpoint(db, room_id, setpoint)
    return fastapi.responses.RedirectResponse(url='/heaters/', status_code=303)