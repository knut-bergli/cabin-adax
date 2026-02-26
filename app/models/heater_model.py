from pydantic import BaseModel


class Heater(BaseModel):
    id: str
    name: str
    type: str  # 'Adax' or 'Mill'
    current_temp: float
    setpoint: float
    is_on: bool = True

    def __repr__(self):
        return f"Heater(id={self.id}, name='{self.name}', type='{self.type}', current_temp={self.current_temp}, setpoint={self.setpoint}, is_on={self.is_on})"

    def __str__(self):
        return f"Heater: {self.name} ({self.type}) - Temp: {self.current_temp}°C, Setpoint: {self.setpoint}°C, {'On' if self.is_on else 'Off'}"

