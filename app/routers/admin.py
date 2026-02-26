import fastapi
from fastapi import Form, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_chameleon import template
from app.services import data_service
from app.models.db_session import db_dependency
from app.models.room_model import Room
from app.models.heater_model import Heater

router = fastapi.APIRouter(prefix="/admin")

@router.get('/rooms')
@template(template_file='admin/rooms.pt')
async def rooms_list(db: db_dependency):
    rooms = await data_service.get_rooms(db)
    return {'rooms': rooms}

@router.get('/rooms/add')
@template(template_file='admin/edit_room.pt')
async def add_room_get():
    return {'room': None}

@router.post('/rooms/add')
async def add_room_post(id: str = Form(...), name: str = Form(...), db: db_dependency = None):
    room = Room(id=id, name=name)
    await data_service.add_room(db, room)
    return RedirectResponse(url='/admin/rooms', status_code=303)

@router.get('/rooms/edit/{room_id}')
@template(template_file='admin/edit_room.pt')
async def edit_room_get(room_id: str, db: db_dependency):
    room = await data_service.get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return {'room': room}

@router.post('/rooms/edit/{room_id}')
async def edit_room_post(room_id: str, name: str = Form(...), db: db_dependency = None):
    await data_service.update_room(db, room_id, name)
    return RedirectResponse(url='/admin/rooms', status_code=303)

@router.post('/rooms/delete/{room_id}')
async def delete_room(room_id: str, db: db_dependency):
    await data_service.delete_room(db, room_id)
    return RedirectResponse(url='/admin/rooms', status_code=303)

@router.get('/heaters')
@template(template_file='admin/heaters.pt')
async def heaters_list(db: db_dependency):
    heaters = await data_service.get_heaters(db)
    return {'heaters': heaters}

@router.get('/heaters/add')
@template(template_file='admin/edit_heater.pt')
async def add_heater_get(db: db_dependency):
    rooms = await data_service.get_rooms(db)
    return {'heater': None, 'rooms': rooms}

@router.post('/heaters/add')
async def add_heater_post(
    id: str = Form(...), 
    name: str = Form(...), 
    type: str = Form(...),
    current_temp: float = Form(0.0),
    setpoint: float = Form(20.0),
    is_on: bool = Form(True),
    room_id: str = Form(None),
    db: db_dependency = None
):
    heater = Heater(id=id, name=name, type=type, current_temp=current_temp, setpoint=setpoint, is_on=is_on, room_id=room_id)
    await data_service.add_heater(db, heater)
    return RedirectResponse(url='/admin/heaters', status_code=303)

@router.get('/heaters/edit/{heater_id}')
@template(template_file='admin/edit_heater.pt')
async def edit_heater_get(heater_id: str, db: db_dependency):
    heater = await data_service.get_heater_by_id(db, heater_id)
    if not heater:
        raise HTTPException(status_code=404, detail="Heater not found")
    rooms = await data_service.get_rooms(db)
    return {'heater': heater, 'rooms': rooms}

@router.post('/heaters/edit/{heater_id}')
async def edit_heater_post(
    heater_id: str,
    name: str = Form(...),
    type: str = Form(...),
    current_temp: float = Form(...),
    setpoint: float = Form(...),
    is_on: bool = Form(False),
    room_id: str = Form(None),
    db: db_dependency = None
):
    await data_service.update_heater(db, heater_id, name, type, current_temp, setpoint, is_on, room_id)
    return RedirectResponse(url='/admin/heaters', status_code=303)

@router.post('/heaters/delete/{heater_id}')
async def delete_heater(heater_id: str, db: db_dependency):
    await data_service.delete_heater(db, heater_id)
    return RedirectResponse(url='/admin/heaters', status_code=303)
