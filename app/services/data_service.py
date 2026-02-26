import json
import os

from app.models.room_model import Room
from app.models.heater_model import Heater


# Load rooms from JSON file
def _load_rooms_from_json():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rooms.json')
    with open(json_path, 'r') as f:
        data = json.load(f)

    rooms_list = []
    for room_data in data['rooms']:
        heaters = [
            Heater(
                id=h['id'],
                name=h['name'],
                type=h['type'],
                current_temp=h['current_temp'],
                setpoint=h['setpoint']
            )
            for h in room_data['heaters']
        ]
        rooms_list.append(Room(
            id=room_data['id'],
            name=room_data['name'],
            heaters=heaters
        ))
    return rooms_list


rooms = _load_rooms_from_json()


def get_rooms():
    return rooms


def update_room_setpoint(room_id: str, new_setpoint: float):
    for room in rooms:
        if room.id == room_id:
            for heater in room.heaters:
                heater.setpoint = new_setpoint
            return True
    return False
