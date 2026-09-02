import asyncio
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import chameleon

from app.main import app, configure
from app.models.room_model import Room
from app.models.heater_model import Heater
from app.services import heater_service, data_service
from app.routers import heaters_dashboard


async def test_heater_service_and_models():
    print("Testing Heater model...")
    heater1 = Heater(
        id=1,
        name="Living Room Heater",
        type="Adax",
        ip_address="192.168.1.50",
        token="token123",
        is_on=True
    )
    heater2 = Heater(
        id=2,
        name="Kitchen Heater",
        type="Adax",
        ip_address="192.168.1.51",
        token="token456",
        is_on=False
    )
    room = Room(id=1, name="Living Room", heaters=[heater1, heater2])

    assert heater1.current_temp == 20.0
    assert heater1.setpoint == 20.0
    assert room.average_temp == 20.0
    assert room.current_setpoint == 20.0

    print("Testing boilerplate AdaxLocalClient and service functions...")
    temp = await heater_service.read_heater_temperature(heater1)
    assert temp == 21.5
    assert heater1.current_temp == 21.5

    setpoint = await heater_service.read_heater_setpoint(heater1)
    assert setpoint == 22.0
    assert heater1.setpoint == 22.0

    success = await heater_service.set_heater_setpoint(heater1, 23.5)
    assert success is True
    assert heater1.setpoint == 23.5

    heater2.current_temp = 19.5
    heater2.setpoint = 23.5
    assert room.average_temp == (21.5 + 19.5) / 2
    assert room.current_setpoint == 23.5

    print("Testing refresh_rooms_heaters...")
    await heater_service.refresh_rooms_heaters([room])
    assert heater1.current_temp == 21.5
    assert heater2.current_temp == 21.5


async def test_database_and_routes():
    print("Testing database and router endpoints...")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        room = Room(name="Stue")
        session.add(room)
        await session.commit()
        await session.refresh(room)

        heater1 = Heater(name="Panel 1", type="Adax", ip_address="192.168.1.10", token="t1", is_on=True, room_id=room.id)
        heater2 = Heater(name="Panel 2", type="Adax", ip_address="192.168.1.11", token="t2", is_on=False, room_id=room.id)
        session.add(heater1)
        session.add(heater2)
        await session.commit()

        # Test index route endpoint
        configure(dev_mode=True)
        response = await heaters_dashboard.index(session)
        assert response.status_code == 200
        html = response.body.decode("utf-8")
        assert "Stue" in html
        assert "Panel 1" in html
        assert "Panel 2" in html
        assert "21.5" in html
        assert "22.0" in html
        assert "/heaters/set_temp/1" in html
        assert "ON" in html

        # Test with an OFF heater
        heater2.is_on = False
        import fastapi_chameleon.engine
        rendered = fastapi_chameleon.engine.render("heaters_dashboard/heaters_dashboard.pt", rooms=[room])
        assert "OFF" in rendered

        # Test set_temp route endpoint
        response = await heaters_dashboard.set_temp(room.id, session, setpoint=24.5)
        assert response.status_code == 303
        assert response.headers["location"] == "/heaters/"

        # Verify heaters in DB were updated
        rooms = await data_service.get_rooms(session, refresh_heaters=False)
        assert len(rooms) == 1
        for h in rooms[0].heaters:
            assert h.setpoint == 24.5


if __name__ == "__main__":
    asyncio.run(test_heater_service_and_models())
    asyncio.run(test_database_and_routes())
    print("ALL TESTS PASSED SUCCESSFULLY!")
