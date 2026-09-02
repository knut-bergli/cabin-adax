import logging
from typing import Sequence, Dict, Any
from app.models.heater_model import Heater
from app.models.room_model import Room

logger = logging.getLogger(__name__)


class AdaxLocalClient:
    """
    Boilerplate client for local communication with Adax heaters.
    
    Adax Wi-Fi heaters on the local network can be communicated with directly
    using their IP address and authentication token.
    """

    @staticmethod
    async def get_temperature(ip_address: str, token: str) -> float:
        """
        Read the actual/ambient temperature from the Adax heater via local communication.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.

        Returns:
            float: The measured ambient temperature in degrees Celsius.
        """
        # =====================================================================
        # TODO: Add actual local communication with Adax heater here.
        # Example (HTTP / REST / Socket):
        #   url = f"http://{ip_address}/api/v1/temperature"
        #   headers = {"Authorization": f"Bearer {token}"}
        #   async with httpx.AsyncClient() as client:
        #       response = await client.get(url, headers=headers, timeout=5.0)
        #       data = response.json()
        #       return float(data.get("target_temperature", 20.0))
        # =====================================================================
        logger.debug(f"[AdaxLocalClient] Reading temperature from heater at {ip_address}")
        # Default / simulated temperature (fallback)
        return 21.5

    @staticmethod
    async def get_setpoint(ip_address: str, token: str) -> float:
        """
        Read the current setpoint (target temperature) from the Adax heater.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.

        Returns:
            float: The target setpoint temperature in degrees Celsius.
        """
        # =====================================================================
        # TODO: Add actual local communication with Adax heater here.
        # Example:
        #   url = f"http://{ip_address}/api/v1/setpoint"
        #   headers = {"Authorization": f"Bearer {token}"}
        #   async with httpx.AsyncClient() as client:
        #       response = await client.get(url, headers=headers, timeout=5.0)
        #       data = response.json()
        #       return float(data.get("setpoint", 22.0))
        # =====================================================================
        logger.debug(f"[AdaxLocalClient] Reading setpoint from heater at {ip_address}")
        # Default / simulated setpoint (fallback)
        return 22.0

    @staticmethod
    async def set_setpoint(ip_address: str, token: str, new_setpoint: float) -> bool:
        """
        Send a new setpoint (target temperature) to the Adax heater.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.
            new_setpoint: Target temperature in degrees Celsius to set on the heater.

        Returns:
            bool: True if the setpoint was successfully updated, False otherwise.
        """
        # =====================================================================
        # TODO: Add actual local communication with Adax heater here.
        # Example:
        #   url = f"http://{ip_address}/api/v1/setpoint"
        #   headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        #   payload = {"setpoint": new_setpoint}
        #   async with httpx.AsyncClient() as client:
        #       response = await client.post(url, json=payload, headers=headers, timeout=5.0)
        #       return response.status_code == 200
        # =====================================================================
        logger.info(f"[AdaxLocalClient] Sending new setpoint {new_setpoint}°C to heater at {ip_address}")
        return True

    @staticmethod
    async def get_status(ip_address: str, token: str) -> Dict[str, Any]:
        """
        Read complete status (temperature, setpoint, power status) from the Adax heater.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.

        Returns:
            dict: Dictionary with temperature, setpoint, and is_on state.
        """
        # =====================================================================
        # TODO: Add actual local communication with Adax heater here.
        # Example:
        #   url = f"http://{ip_address}/api/v1/status"
        #   headers = {"Authorization": f"Bearer {token}"}
        #   async with httpx.AsyncClient() as client:
        #       response = await client.get(url, headers=headers, timeout=5.0)
        #       return response.json()
        # =====================================================================
        logger.debug(f"[AdaxLocalClient] Reading status from heater at {ip_address}")
        return {
            "current_temp": 21.5,
            "setpoint": 22.0,
            "is_on": True,
        }


# High-level helper functions operating on Heater and Room models

async def read_heater_temperature(heater: Heater) -> float:
    """
    Read the actual temperature from a heater.
    """
    try:
        temp = await AdaxLocalClient.get_temperature(heater.ip_address, heater.token)
        heater.current_temp = temp
        return temp
    except Exception as e:
        logger.error(f"Failed to read temperature from heater {heater.name} ({heater.ip_address}): {e}")
        return heater.current_temp


async def read_heater_setpoint(heater: Heater) -> float:
    """
    Read the setpoint from a heater.
    """
    try:
        setpoint = await AdaxLocalClient.get_setpoint(heater.ip_address, heater.token)
        heater.setpoint = setpoint
        return setpoint
    except Exception as e:
        logger.error(f"Failed to read setpoint from heater {heater.name} ({heater.ip_address}): {e}")
        return heater.setpoint


async def set_heater_setpoint(heater: Heater, new_setpoint: float) -> bool:
    """
    Send a new setpoint to a heater.
    """
    try:
        success = await AdaxLocalClient.set_setpoint(heater.ip_address, heater.token, new_setpoint)
        if success:
            heater.setpoint = new_setpoint
        return success
    except Exception as e:
        logger.error(f"Failed to set setpoint {new_setpoint} on heater {heater.name} ({heater.ip_address}): {e}")
        return False


async def refresh_heater_data(heater: Heater) -> Heater:
    """
    Fetch both current temperature and setpoint from the physical heater and update the model instance.
    """
    try:
        status = await AdaxLocalClient.get_status(heater.ip_address, heater.token)
        if "current_temp" in status:
            heater.current_temp = float(status["current_temp"])
        if "setpoint" in status:
            heater.setpoint = float(status["setpoint"])
        if "is_on" in status:
            heater.is_on = bool(status["is_on"])
    except Exception as e:
        logger.error(f"Failed to refresh heater {heater.name} ({heater.ip_address}): {e}")
    return heater


async def refresh_room_heaters(room: Room) -> Room:
    """
    Refresh temperature and setpoint data for all heaters in a room.
    """
    if room and room.heaters:
        for heater in room.heaters:
            await refresh_heater_data(heater)
    return room


async def refresh_rooms_heaters(rooms: Sequence[Room]) -> Sequence[Room]:
    """
    Refresh temperature and setpoint data for all heaters across multiple rooms.
    """
    for room in rooms:
        await refresh_room_heaters(room)
    return rooms
