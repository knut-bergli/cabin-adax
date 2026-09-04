import asyncio
from unittest.mock import patch, AsyncMock
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

    assert heater1.is_available is True
    assert heater1.current_temp == 20.0
    assert heater1.setpoint == 20.0
    assert room.average_temp == 20.0
    assert room.current_setpoint == 20.0
    assert room.has_unavailable_heaters is False

    print("Testing AdaxLocalClient and service functions with mocked Adax...")
    # Mock Adax responses for successful client communication
    with patch("app.services.heater_service.Adax") as mock_adax_cls:
        mock_instance = AsyncMock()
        mock_instance.get_status.return_value = {
            "current_temperature": 21.5,
            "target_temperature": 22.0
        }
        mock_instance.set_target_temperature.return_value = 200
        mock_adax_cls.return_value = mock_instance

        temp = await heater_service.read_heater_temperature(heater1)
        assert temp == 21.5
        assert heater1.current_temp == 21.5
        assert heater1.is_available is True

        setpoint = await heater_service.read_heater_setpoint(heater1)
        assert setpoint == 22.0
        assert heater1.setpoint == 22.0
        assert heater1.is_available is True

        success = await heater_service.set_heater_setpoint(heater1, 23.5)
        assert success is True
        assert heater1.setpoint == 23.5
        assert heater1.is_available is True

    # Test handling when heater is unavailable / offline
    print("Testing unavailable heater handling...")
    heater_unavailable = Heater(
        id=3,
        name="Bedroom Heater",
        type="Adax",
        ip_address="192.168.1.99",
        token="token999",
        is_on=True
    )
    with patch("app.services.heater_service.Adax") as mock_adax_cls:
        mock_instance = AsyncMock()
        # Adax returns None for temperatures on timeout/failure
        mock_instance.get_status.return_value = {
            "current_temperature": None,
            "target_temperature": None
        }
        mock_instance.set_target_temperature.return_value = 500
        mock_adax_cls.return_value = mock_instance

        status = await heater_service.AdaxLocalClient.get_status("192.168.1.99", "token999")
        assert status["is_available"] is False
        assert status["current_temp"] is None
        assert status["setpoint"] is None
        assert status["is_on"] is False

        await heater_service.refresh_heater_data(heater_unavailable)
        assert heater_unavailable.is_available is False
        assert heater_unavailable.current_temp is None
        assert heater_unavailable.setpoint is None
        assert heater_unavailable.is_on is False

        # Test handling when heater raises connection exception (host down / network error)
        with patch("app.services.heater_service.Adax") as mock_adax_cls:
            mock_instance = AsyncMock()
            mock_instance.get_status.side_effect = Exception("Cannot connect to host: Host is down")
            mock_adax_cls.return_value = mock_instance

            status = await heater_service.AdaxLocalClient.get_status("192.168.1.99", "token999")
            assert status["is_available"] is False
            assert status["current_temp"] is None
            assert status["setpoint"] is None
            assert status["is_on"] is False

            await heater_service.refresh_heater_data(heater_unavailable)
            assert heater_unavailable.is_available is False
            assert heater_unavailable.current_temp is None
            assert heater_unavailable.setpoint is None
            assert heater_unavailable.is_on is False

    # Test room temperature averaging with one available and one unavailable heater
    heater2.current_temp = 19.5
    heater2.setpoint = 23.5
    heater2.is_available = True
    room.heaters = [heater1, heater_unavailable]
    assert room.has_unavailable_heaters is True
    # Average temp should only consider heater1 (21.5°C), ignoring unavailable heater_unavailable
    assert room.average_temp == 21.5
    assert room.current_setpoint == 23.5


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

        # Test index route endpoint with mocked active heaters
        configure(dev_mode=True)
        with patch("app.services.heater_service.Adax") as mock_adax_cls:
            mock_instance = AsyncMock()
            mock_instance.get_status.return_value = {
                "current_temperature": 21.5,
                "target_temperature": 22.0
            }
            mock_instance.set_target_temperature.return_value = 200
            mock_adax_cls.return_value = mock_instance

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
            assert "Auto-refresh:" in html
            assert "Next update:" in html
            assert "Last updated:" in html
            assert "auto-refresh-select" in html
            assert "countdown-display" in html

        # Test rendering with an unavailable / offline heater
        heater2.is_available = False
        heater2.current_temp = None
        heater2.setpoint = None
        heater2.is_on = False
        import fastapi_chameleon.engine
        rendered = fastapi_chameleon.engine.render(
            "heaters_dashboard/heaters_dashboard.pt",
            rooms=[room],
            last_updated="12:34:56",
            refresh_interval=120
        )
        assert "Offline" in rendered
        assert "Unavailable" in rendered
        assert "12:34:56" in rendered
        assert 'data-interval="120"' in rendered
        assert "Auto-refresh:" in rendered
        assert "Next update:" in rendered
        assert "btn-manual-refresh" in rendered

        # Test rendering when refresh_interval = 0 (Auto-Refresh, Next update and Refresh should be hidden)
        rendered_zero = fastapi_chameleon.engine.render(
            "heaters_dashboard/heaters_dashboard.pt",
            rooms=[room],
            last_updated="12:34:56",
            refresh_interval=0
        )
        assert "Auto-refresh:" not in rendered_zero
        assert "Next update:" not in rendered_zero
        assert "btn-manual-refresh" not in rendered_zero
        assert "auto-refresh-select" not in rendered_zero
        assert "refresh-countdown-badge" not in rendered_zero

        # Test set_temp route endpoint
        with patch("app.services.heater_service.Adax") as mock_adax_cls:
            mock_instance = AsyncMock()
            mock_instance.set_target_temperature.return_value = 200
            mock_adax_cls.return_value = mock_instance

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
