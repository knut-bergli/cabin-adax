from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.heater_model import Heater


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    heaters: List[Heater] = Relationship(back_populates="room")

    @property
    def available_heaters(self) -> List[Heater]:
        if not self.heaters:
            return []
        return [h for h in self.heaters if getattr(h, "is_available", True)]

    @property
    def has_unavailable_heaters(self) -> bool:
        if not self.heaters:
            return False
        return any(not getattr(h, "is_available", True) for h in self.heaters)

    @property
    def average_temp(self) -> float:
        if not self.heaters:
            return 0.0
        # Calculate average only from available heaters with valid temperatures
        avail_temps = [
            h.current_temp for h in self.heaters
            if getattr(h, "is_available", True) and h.current_temp is not None and h.current_temp != -99
        ]
        if avail_temps:
            return sum(avail_temps) / len(avail_temps)

        # Fallback to any heater with valid temp if all are marked unavailable
        all_temps = [
            h.current_temp for h in self.heaters
            if h.current_temp is not None and h.current_temp != -99
        ]
        if all_temps:
            return sum(all_temps) / len(all_temps)
        return 0.0

    @property
    def current_setpoint(self) -> float:
        # Assuming all heaters in a room should have the same setpoint for simplicity
        if not self.heaters:
            return 20.0
        for h in self.heaters:
            if getattr(h, "is_available", True) and h.setpoint is not None and h.setpoint != -99:
                return h.setpoint
        for h in self.heaters:
            if h.setpoint is not None and h.setpoint != -99:
                return h.setpoint
        return 20.0

    def __repr__(self):
        return f"Room(id={self.id}, name='{self.name}', heaters={len(self.heaters)}, average_temp={self.average_temp:.1f}°C)"

    def __str__(self):
        return f"Room: {self.name} - Average Temp: {self.average_temp:.1f}°C, Setpoint: {self.current_setpoint:.1f}°C"
