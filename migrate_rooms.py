import json
import asyncio
from pathlib import Path
from sqlmodel import Session, create_engine, select
from app.models.room_model import Room
from app.models.heater_model import Heater
from app.config.load_environment import get_settings, resolve_path

def migrate_data():
    # Setup paths
    json_path = resolve_path('app/data/rooms.json')
    db_file = resolve_path('cabin_adax_storage/db') / get_settings().DB_NAME
    
    if not json_path.exists():
        print(f"Error: {json_path} not found.")
        return

    # Use synchronous engine for migration script for simplicity
    conn_str = 'sqlite:///' + str(db_file)
    engine = create_engine(conn_str)
    
    # Create tables
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    with open(json_path, 'r') as f:
        data = json.load(f)

    with Session(engine) as session:
        # Check if data already exists to avoid duplicates
        existing_rooms = session.exec(select(Room)).all()
        if existing_rooms:
            print("Database already contains data. Skipping migration.")
            return

        for room_data in data['rooms']:
            room = Room(
                name=room_data['name']
            )
            session.add(room)
            session.flush() # Ensure room.id is generated
            
            for heater_data in room_data['heaters']:
                heater = Heater(
                    name=heater_data['name'],
                    type=heater_data['type'],
                    current_temp=heater_data['current_temp'],
                    setpoint=heater_data['setpoint'],
                    room_id=room.id
                )
                session.add(heater)
        
        session.commit()
        print(f"Successfully migrated data from {json_path} to {db_file}")

if __name__ == "__main__":
    migrate_data()
