from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.room_model import Room


class Heater(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # 'Adax'
    ip_address: str
    token: str
    is_on: bool = Field(default=True)

    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    room: Optional["Room"] = Relationship(back_populates="heaters")

    # Dynamic/transient properties read from physical heater
    _current_temp: Optional[float] = None
    _setpoint: Optional[float] = None

    @property
    def current_temp(self) -> float:
        if self._current_temp is not None:
            return self._current_temp
        return 20.0

    @current_temp.setter
    def current_temp(self, value: Optional[float]):
        self._current_temp = value

    @property
    def setpoint(self) -> float:
        if self._setpoint is not None:
            return self._setpoint
        return 20.0

    @setpoint.setter
    def setpoint(self, value: Optional[float]):
        self._setpoint = value

    def __repr__(self):
        return f"Heater(id={self.id}, name='{self.name}', type='{self.type}', ip_address= {self.ip_address}, token={self.token})"

    def __str__(self):
        return f"Heater: ({self.name} ({self.type}), , ip_address= {self.ip_address}, token={self.token})"
