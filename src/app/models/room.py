from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum
from typing import Optional


class RoomVariation(str, Enum):
    COUP_O_CLOCK = "coup-o-clock"
    COUP_PAST_COUP = "quarter-past-coup"
    COUP_THIRTY = "coup-thirty"


class RoomSettings(BaseModel):
    addons: list[str]


class Room(BaseModel):
    code: str = Field(default=None)
    owner_id: str
    variation: str
    room_settings: RoomSettings

    class Config:
        json_schema_extra = {
            "example": {
                "variation": "coup-o-clock",
                "room_price": "29.99",
                "room_settings": {"addons": ["timer", "music", "special-cards"]},
            }
        }
