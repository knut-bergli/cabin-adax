from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.heater_model import Heater


class Room(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    heaters: List[Heater] = Relationship(back_populates="room")

    @property
    def average_temp(self) -> float:
        if not self.heaters:
            return 0.0
        return sum(h.current_temp for h in self.heaters) / len(self.heaters)

    @property
    def current_setpoint(self) -> float:
        # Assuming all heaters in a room should have the same setpoint for simplicity
        if not self.heaters:
            return 20.0
        return self.heaters[0].setpoint

    def __repr__(self):
        return f"Room(id={self.id}, name='{self.name}', heaters={len(self.heaters)}, average_temp={self.average_temp:.1f}°C)"

    def __str__(self):
        return f"Room: {self.name} - Average Temp: {self.average_temp:.1f}°C, Setpoint: {self.current_setpoint}°C"
