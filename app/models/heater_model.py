from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.room_model import Room


class Heater(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # 'Adax' or 'Mill'
    ip_address: str
    token: str
    is_on: bool = Field(default=True)

    room_id: Optional[int] = Field(default=None, foreign_key="room.id")
    room: Optional["Room"] = Relationship(back_populates="heaters")

    def __repr__(self):
        return f"Heater(id={self.id}, name='{self.name}', type='{self.type}', ip_address= {self.ip_address}, token={self.token}, is_on={self.is_on})"

    def __str__(self):
        return f"Heater: {self.name} ({self.type}), , ip_address= {self.ip_address}, token={self.token}, {'On' if self.is_on else 'Off'}"

