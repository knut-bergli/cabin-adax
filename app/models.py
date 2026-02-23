from typing import List, Optional
from pydantic import BaseModel


class Heater(BaseModel):
    id: str
    name: str
    type: str  # 'Adax' or 'Mill'
    current_temp: float
    setpoint: float
    is_on: bool = True


class Room(BaseModel):
    id: str
    name: str
    heaters: List[Heater]

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
