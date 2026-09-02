from typing import Sequence

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room_model import Room
from app.models.heater_model import Heater
from app.services import heater_service


async def get_rooms(db: AsyncSession, refresh_heaters: bool = False) -> Sequence[Room]:
    stmt = select(Room).options(selectinload(Room.heaters))
    result = await db.execute(stmt)
    rooms = result.scalars().unique().all()
    if refresh_heaters:
        await heater_service.refresh_rooms_heaters(rooms)
    return rooms


async def get_room_by_id(db: AsyncSession, room_id: int) -> Room | None:
    stmt = select(Room).where(Room.id == room_id).options(selectinload(Room.heaters))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_room(db: AsyncSession, room: Room) -> Room:
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def update_room(db: AsyncSession, room_id: int, name: str) -> Room | None:
    room = await get_room_by_id(db, room_id)
    if not room:
        return None
    room.name = name
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


async def delete_room(db: AsyncSession, room_id: int) -> bool:
    room = await get_room_by_id(db, room_id)
    if not room:
        return False
    await db.delete(room)
    await db.commit()
    return True


async def update_room_setpoint(db: AsyncSession, room_id: int, new_setpoint: float) -> bool:
    # Load heaters for the specified room and update their setpoints
    stmt = (
        select(Heater)
        .join(Room, Room.id == Heater.room_id)
        .where(Room.id == room_id)
    )
    result = await db.execute(stmt)
    heaters = result.scalars().all()
    if not heaters:
        return False

    for h in heaters:
        # Change setpoint for each heater in the room
        await heater_service.set_heater_setpoint(h, new_setpoint)

    await db.commit()
    return True


async def get_heaters(db: AsyncSession) -> Sequence[Heater]:
    stmt = select(Heater).options(selectinload(Heater.room))
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_heater_by_id(db: AsyncSession, heater_id: int) -> Heater | None:
    stmt = select(Heater).where(Heater.id == heater_id).options(selectinload(Heater.room))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_heater(db: AsyncSession, heater: Heater) -> Heater:
    db.add(heater)
    await db.commit()
    await db.refresh(heater)
    return heater


async def update_heater(db: AsyncSession, heater_id: int, name: str, type: str, ip_address: str, token: str,
                        room_id: int | None) -> Heater | None:
    heater = await get_heater_by_id(db, heater_id)
    if not heater:
        return None
    heater.name = name
    heater.type = type
    heater.ip_address = ip_address
    heater.token = token
    heater.room_id = room_id
    db.add(heater)
    await db.commit()
    await db.refresh(heater)
    return heater


async def delete_heater(db: AsyncSession, heater_id: int) -> bool:
    heater = await get_heater_by_id(db, heater_id)
    if not heater:
        return False
    await db.delete(heater)
    await db.commit()
    return True
