from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class RoomVariation(str, Enum):
    COUP_O_CLOCK = "coup-o-clock"
    COUP_PAST_COUP = "quarter-past-coup"
    COUP_THIRTY = "coup-thirty"


class RoomSettings(BaseModel):
    addons: list[str]


class Player(BaseModel):
    id: str
    name: str
    is_ready: bool = False


class Room(BaseModel):
    code: str = Field(default=None)
    owner_id: str
    variation: str
    room_settings: RoomSettings
    players: List[Player] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "variation": "coup-o-clock",
                "room_price": "29.99",
                "room_settings": {"addons": ["timer", "music", "special-cards"]},
                "players": [],
            }
        }
