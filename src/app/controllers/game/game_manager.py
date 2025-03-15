from app.models.game import GameState, PlayerState, GameStatus
from typing import Dict, Optional, List
import random
import uuid


class GameManager:
    def __init__(self):
        # Map of room_code -> GameState
        self.games: Dict[str, GameState] = {}

    def create_game(self, room_code: str, player_names: List[str]) -> GameState:
        """Create a new game for a room"""
        if room_code in self.games:
            return self.games[room_code]

        # Create player states
        players = []
        for name in player_names:
            player_id = str(uuid.uuid4())
            players.append(PlayerState(id=player_id, name=name))

        # Create game state
        game_state = GameState(
            room_code=room_code,
            players=players,
            deck=self._create_deck(),
            status=GameStatus.WAITING,
        )

        self.games[room_code] = game_state
        return game_state

    def start_game(self, room_code: str) -> Optional[GameState]:
        """Start a game in a room"""
        if room_code not in self.games:
            return None

        game = self.games[room_code]

        # Shuffle the deck
        random.shuffle(game.deck)

        # Deal cards to players
        for player in game.players:
            player.cards = [game.deck.pop() for _ in range(2)]

        # Set game status to playing
        game.status = GameStatus.PLAYING

        return game

    def get_game(self, room_code: str) -> Optional[GameState]:
        """Get the game state for a room"""
        return self.games.get(room_code)

    def remove_game(self, room_code: str) -> bool:
        """Remove a game from the manager"""
        if room_code in self.games:
            del self.games[room_code]
            return True
        return False

    def _create_deck(self) -> List[str]:
        """Create a deck of cards for the game"""
        # In Coup, there are 3 copies of each character card
        cards = []
        characters = ["duke", "assassin", "captain", "ambassador", "contessa"]
        for character in characters:
            cards.extend([character] * 3)

        random.shuffle(cards)
        return cards

    def get_player_view(self, room_code: str, player_id: str) -> dict:
        """Get a view of the game state for a specific player"""
        game = self.get_game(room_code)
        if not game:
            return {"error": "Game not found"}

        # Find the player
        player = next((p for p in game.players if p.id == player_id), None)
        if not player:
            return {"error": "Player not found"}

        # Create a view that hides other players' cards
        other_players = []
        for p in game.players:
            if p.id == player_id:
                # Include full player info for the requesting player
                other_players.append(p.dict())
            else:
                # Hide cards for other players
                player_info = p.dict()
                player_info["cards"] = ["hidden"] * len(p.cards)
                other_players.append(player_info)

        return {
            "room_code": game.room_code,
            "status": game.status,
            "players": other_players,
            "current_player_index": game.current_player_index,
            "current_player": (
                game.players[game.current_player_index].name if game.players else None
            ),
            "is_your_turn": (
                game.players[game.current_player_index].id == player_id
                if game.players
                else False
            ),
            "turn_number": game.turn_number,
            "last_action": game.last_action,
            "cards_left": len(game.deck),
        }


# Create a singleton instance
manager = GameManager()
