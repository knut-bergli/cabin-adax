import asyncio
import logging
from typing import Sequence, Dict, Any, Optional
from app.models.heater_model import Heater
from app.models.room_model import Room

import aiohttp
from adax_local import Adax

logger = logging.getLogger(__name__)


class AdaxLocalClient:
    """
    Boilerplate client for local communication with Adax heaters.
    
    Adax Wi-Fi heaters on the local network can be communicated with directly
    using their IP address and authentication token.
    """

    @staticmethod
    async def get_temperature(ip_address: str, token: str) -> Optional[float]:
        """
        Read the actual/ambient temperature from the Adax heater via local communication.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.

        Returns:
            Optional[float]: The measured ambient temperature in degrees Celsius, or None if unavailable.
        """
        logger.debug(f"[AdaxLocalClient] Reading temperature from heater at {ip_address}")
        connector = aiohttp.TCPConnector(ssl=False)
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                heater = Adax(ip_address, token, session)
                status = await heater.get_status()
                if status and status.get("current_temperature") is not None:
                    return float(status["current_temperature"])
                logger.warning(f"[AdaxLocalClient] No temperature data received from {ip_address}: {status}")
                return None
        except Exception as e:
            logger.error(f"[AdaxLocalClient] Failed to read temperature from heater at {ip_address}: {e}")
            return None

    @staticmethod
    async def get_setpoint(ip_address: str, token: str) -> Optional[float]:
        """
        Read the current setpoint (target temperature) from the Adax heater.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.

        Returns:
            Optional[float]: The target setpoint temperature in degrees Celsius, or None if unavailable.
        """
        logger.debug(f"[AdaxLocalClient] Reading setpoint from heater at {ip_address}")
        connector = aiohttp.TCPConnector(ssl=False)
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                heater = Adax(ip_address, token, session)
                status = await heater.get_status()
                if status and status.get("target_temperature") is not None:
                    return float(status["target_temperature"])
                logger.warning(f"[AdaxLocalClient] No setpoint data received from {ip_address}: {status}")
                return None
        except Exception as e:
            logger.error(f"[AdaxLocalClient] Failed to read setpoint from heater at {ip_address}: {e}")
            return None

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
        logger.info(f"[AdaxLocalClient] Sending new setpoint {new_setpoint}°C to heater at {ip_address}")
        connector = aiohttp.TCPConnector(ssl=False)
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                heater = Adax(ip_address, token, session)
                status_code = await heater.set_target_temperature(new_setpoint)
                if status_code == 200:
                    logger.info(f"[AdaxLocalClient] Successfully updated setpoint on {ip_address}")
                    return True
                logger.warning(f"[AdaxLocalClient] Non-200 response ({status_code}) setting setpoint on {ip_address}")
                return False
        except Exception as e:
            logger.error(f"[AdaxLocalClient] Failed to send setpoint to heater at {ip_address}: {e}")
            return False

    @staticmethod
    async def get_status(ip_address: str, token: str) -> Dict[str, Any]:
        """
        Read complete status (temperature, setpoint, power status) from the Adax heater.

        Args:
            ip_address: IP address of the Adax heater on the local network.
            token: Authentication token / key for the heater.

        Returns:
            dict: Dictionary with is_available, current_temp, setpoint, and is_on state.
        """
        logger.debug(f"[AdaxLocalClient] Reading status from heater at {ip_address}")
        connector = aiohttp.TCPConnector(ssl=False)
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                heater = Adax(ip_address, token, session)
                status = await heater.get_status()
                logger.info("--- Adax Heater Status ---")
                logger.info(f"Status Data: {status}")

                if not status or status.get("current_temperature") is None or status.get("target_temperature") is None:
                    logger.warning(f"Adax heater at {ip_address} is unavailable or returned incomplete data: {status}")
                    return {
                        "is_available": False,
                        "available": False,
                        "current_temp": None,
                        "setpoint": None,
                        "is_on": False,
                    }

                current_temp = float(status["current_temperature"])
                target_temp = float(status["target_temperature"])

                logger.info(f"Current Temperature: {current_temp}°C")
                logger.info(f"Target Temperature:  {target_temp}°C")

                return {
                    "is_available": True,
                    "available": True,
                    "current_temp": current_temp,
                    "setpoint": target_temp,
                    "is_on": True,
                }
        except Exception as e:
            logger.error(f"[AdaxLocalClient] Error communicating with heater at {ip_address}: {e}")
            return {
                "is_available": False,
                "available": False,
                "current_temp": None,
                "setpoint": None,
                "is_on": False,
            }


# High-level helper functions operating on Heater and Room models

async def read_heater_temperature(heater: Heater) -> Optional[float]:
    """
    Read the actual temperature from a heater.
    """
    try:
        temp = await AdaxLocalClient.get_temperature(heater.ip_address, heater.token)
        if temp is not None:
            heater.current_temp = temp
            heater.is_available = True
            return temp
        else:
            heater.is_available = False
            return None
    except Exception as e:
        logger.error(f"Failed to read temperature from heater {heater.name} ({heater.ip_address}): {e}")
        heater.is_available = False
        return None


async def read_heater_setpoint(heater: Heater) -> Optional[float]:
    """
    Read the setpoint from a heater.
    """
    try:
        setpoint = await AdaxLocalClient.get_setpoint(heater.ip_address, heater.token)
        if setpoint is not None:
            heater.setpoint = setpoint
            heater.is_available = True
            return setpoint
        else:
            heater.is_available = False
            return None
    except Exception as e:
        logger.error(f"Failed to read setpoint from heater {heater.name} ({heater.ip_address}): {e}")
        heater.is_available = False
        return None


async def set_heater_setpoint(heater: Heater, new_setpoint: float) -> bool:
    """
    Send a new setpoint to a heater.
    """
    try:
        success = await AdaxLocalClient.set_setpoint(heater.ip_address, heater.token, new_setpoint)
        if success:
            heater.setpoint = new_setpoint
            heater.is_available = True
        else:
            heater.is_available = False
        return success
    except Exception as e:
        logger.error(f"Failed to set setpoint {new_setpoint} on heater {heater.name} ({heater.ip_address}): {e}")
        heater.is_available = False
        return False


async def refresh_heater_data(heater: Heater) -> Heater:
    """
    Fetch both current temperature and setpoint from the physical heater and update the model instance.
    """
    try:
        status = await AdaxLocalClient.get_status(heater.ip_address, heater.token)
        is_available = bool(status.get("is_available", False))
        heater.is_available = is_available
        if is_available:
            if status.get("current_temp") is not None:
                heater.current_temp = float(status["current_temp"])
            if status.get("setpoint") is not None:
                heater.setpoint = float(status["setpoint"])
            if "is_on" in status:
                heater.is_on = bool(status["is_on"])
        else:
            heater.is_on = False
            heater.current_temp = None
            heater.setpoint = None
    except Exception as e:
        logger.error(f"Failed to refresh heater {heater.name} ({heater.ip_address}): {e}")
        heater.is_available = False
        heater.is_on = False
        heater.current_temp = None
        heater.setpoint = None
    return heater


async def refresh_room_heaters(room: Room) -> Room:
    """
    Refresh temperature and setpoint data for all heaters in a room concurrently.
    """
    if room and room.heaters:
        await asyncio.gather(*(refresh_heater_data(heater) for heater in room.heaters), return_exceptions=True)
    return room


async def refresh_rooms_heaters(rooms: Sequence[Room]) -> Sequence[Room]:
    """
    Refresh temperature and setpoint data for all heaters across multiple rooms concurrently.
    """
    if rooms:
        all_heaters = [heater for room in rooms if room and room.heaters for heater in room.heaters]
        if all_heaters:
            await asyncio.gather(*(refresh_heater_data(heater) for heater in all_heaters), return_exceptions=True)
    return rooms
