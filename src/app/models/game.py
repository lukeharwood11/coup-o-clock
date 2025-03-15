from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class GameStatus(str, Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


class PlayerState(BaseModel):
    id: str
    name: str
    coins: int = 2  # Starting coins
    cards: List[str] = Field(default_factory=list)
    revealed_cards: List[str] = Field(default_factory=list)
    is_alive: bool = True


class GameState(BaseModel):
    room_code: str
    status: GameStatus = GameStatus.WAITING
    players: List[PlayerState] = Field(default_factory=list)
    current_player_index: int = 0
    deck: List[str] = Field(default_factory=list)
    discard_pile: List[str] = Field(default_factory=list)
    turn_number: int = 0
    last_action: Optional[Dict] = None

    def is_game_over(self) -> bool:
        """Check if the game is over (only one player alive)"""
        alive_players = [p for p in self.players if p.is_alive]
        return len(alive_players) <= 1

    def get_current_player(self) -> Optional[PlayerState]:
        """Get the current player"""
        if not self.players or self.current_player_index >= len(self.players):
            return None
        return self.players[self.current_player_index]

    def next_player(self) -> PlayerState:
        """Move to the next player and return that player"""
        if not self.players:
            return None

        # Find next alive player
        original_index = self.current_player_index
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
            if self.players[self.current_player_index].is_alive:
                break
            # If we've gone full circle and found no alive players, stay on original
            if self.current_player_index == original_index:
                break

        self.turn_number += 1
        return self.players[self.current_player_index]
