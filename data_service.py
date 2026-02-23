from models import Room, Heater

# Mock data
rooms = [
    Room(id="kitchen", name="Kitchen", heaters=[
        Heater(id="adax-1", name="Kitchen Window", type="Adax", current_temp=21.5, setpoint=22.0),
    ]),
    Room(id="living", name="Living Room", heaters=[
        Heater(id="mill-1", name="Main Wall", type="Mill", current_temp=20.8, setpoint=21.0),
        Heater(id="adax-2", name="Side Wall", type="Adax", current_temp=20.5, setpoint=21.0),
    ]),
    Room(id="bath", name="Bathroom", heaters=[
        Heater(id="adax-3", name="Floor Heater", type="Adax", current_temp=23.2, setpoint=24.0),
    ]),
    Room(id="bedroom1", name="Bedroom 1", heaters=[
        Heater(id="mill-2", name="Bedroom 1 Heater", type="Mill", current_temp=18.5, setpoint=19.0),
    ]),
    Room(id="bedroom2", name="Bedroom 2", heaters=[
        Heater(id="mill-3", name="Bedroom 2 Heater", type="Adax", current_temp=17.5, setpoint=18.0),
    ]),
]


def get_rooms():
    return rooms


def update_room_setpoint(room_id: str, new_setpoint: float):
    for room in rooms:
        if room.id == room_id:
            for heater in room.heaters:
                heater.setpoint = new_setpoint
            return True
    return False
