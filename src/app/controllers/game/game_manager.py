from app.models.game import GameState, PlayerState, GameStatus
from app.controllers.game.coup_game import CoupGame
from typing import Dict, Optional, List
import random
import uuid
import logging


class GameManager:
    def __init__(self):
        # Map of room_code -> GameState
        self.games: Dict[str, GameState] = {}
        # Map of room_code -> CoupGame
        self.coup_games: Dict[str, CoupGame] = {}

    def create_game(self, room_code: str, player_info: List[Dict]) -> GameState:
        """Create a new game for a room"""
        if room_code in self.games:
            return self.games[room_code]

        # Create player states
        players = []
        for player in player_info:
            players.append(PlayerState(id=player["id"], name=player["name"]))

        # Create game state
        game_state = GameState(
            room_code=room_code,
            players=players,
            deck=[],  # Will be created by CoupGame
            status=GameStatus.WAITING,
        )

        self.games[room_code] = game_state

        # Create Coup game
        coup_game = CoupGame(game_state)
        self.coup_games[room_code] = coup_game

        # Create deck
        game_state.deck = coup_game.create_deck()

        return game_state

    def start_game(self, room_code: str) -> Optional[GameState]:
        """Start a game in a room"""
        if room_code not in self.games or room_code not in self.coup_games:
            return None

        game = self.games[room_code]
        coup_game = self.coup_games[room_code]

        # Deal cards to players
        coup_game.deal_cards()

        # Set game status to playing
        game.status = GameStatus.PLAYING

        return game

    def get_game(self, room_code: str) -> Optional[GameState]:
        """Get the game state for a room"""
        return self.games.get(room_code)

    def get_coup_game(self, room_code: str) -> Optional[CoupGame]:
        """Get the Coup game for a room"""
        return self.coup_games.get(room_code)

    def remove_game(self, room_code: str) -> bool:
        """Remove a game from the manager"""
        if room_code in self.games:
            del self.games[room_code]
            if room_code in self.coup_games:
                del self.coup_games[room_code]
            return True
        return False

    def perform_action(self, room_code: str, player_id: str, action: Dict) -> Dict:
        """Perform a game action"""
        logger = logging.getLogger(__name__)

        logger.info(
            f"Performing action: {action} for player {player_id} in room {room_code}"
        )

        coup_game = self.get_coup_game(room_code)
        if not coup_game:
            logger.error(f"Game not found for room {room_code}")
            return {"success": False, "message": "Game not found"}

        # Validate the action
        is_valid, error_message = coup_game.is_action_valid(player_id, action)
        if not is_valid:
            logger.error(f"Invalid action: {error_message}")
            return {"success": False, "message": error_message}

        # Perform the action
        result = coup_game.perform_action(player_id, action)
        logger.info(f"Action result: {result}")
        return result

    def challenge_action(self, room_code: str, challenger_id: str) -> Dict:
        """Challenge a pending action"""
        coup_game = self.get_coup_game(room_code)
        if not coup_game:
            return {"success": False, "message": "Game not found"}

        if not coup_game.challenge_window_open:
            return {"success": False, "message": "No action to challenge"}

        # If there's a pending counteraction, challenge that instead
        if coup_game.pending_counteraction:
            return coup_game.resolve_counteraction_challenge(challenger_id, True)

        # Otherwise challenge the main action
        return coup_game.resolve_challenge(challenger_id, True)

    def pass_challenge(self, room_code: str, player_id: str) -> Dict:
        """Pass on challenging an action"""
        coup_game = self.get_coup_game(room_code)
        if not coup_game:
            return {"success": False, "message": "Game not found"}

        if not coup_game.challenge_window_open:
            return {"success": False, "message": "No action to challenge"}

        # If there's a pending counteraction and all players passed, the counteraction succeeds
        if coup_game.pending_counteraction:
            action_player_id = coup_game.pending_action["player_id"]
            action_player = next(
                (p for p in coup_game.game_state.players if p.id == action_player_id),
                None,
            )

            counter_player_id = coup_game.pending_counteraction["player_id"]
            counter_player = next(
                (p for p in coup_game.game_state.players if p.id == counter_player_id),
                None,
            )

            # If it was an assassination, return the coins
            if coup_game.pending_action["action"].get("action_type") == "assassinate":
                action_player.coins += 3

            # Close windows and clear pending actions
            coup_game.challenge_window_open = False
            coup_game.counteraction_window_open = False
            coup_game.pending_action = None
            coup_game.pending_counteraction = None

            # Move to next player
            coup_game.game_state.next_player()

            return {
                "success": True,
                "message": f"No one challenged. {counter_player.name}'s counteraction succeeds. Action blocked.",
            }

        # If there's a pending action and all players passed, execute the action
        if coup_game.pending_action:
            action_player_id = coup_game.pending_action["player_id"]
            action = coup_game.pending_action["action"]

            # Execute the action
            result = coup_game._execute_action(action_player_id, action)

            # Close challenge window and clear pending action
            coup_game.challenge_window_open = False
            coup_game.pending_action = None

            return {
                "success": True,
                "message": "No one challenged. Action succeeds.",
                "action_result": result,
            }

        return {"success": False, "message": "No pending action"}

    def counter_action(
        self, room_code: str, counter_player_id: str, counter_action: Dict
    ) -> Dict:
        """Counter a pending action"""
        coup_game = self.get_coup_game(room_code)
        if not coup_game:
            return {"success": False, "message": "Game not found"}

        if not coup_game.counteraction_window_open:
            return {"success": False, "message": "No action to counter"}

        return coup_game.resolve_counteraction(counter_player_id, counter_action)

    def pass_counter(self, room_code: str, player_id: str) -> Dict:
        """Pass on countering an action"""
        coup_game = self.get_coup_game(room_code)
        if not coup_game:
            return {"success": False, "message": "Game not found"}

        if not coup_game.counteraction_window_open:
            return {"success": False, "message": "No action to counter"}

        # If all players passed, execute the action
        if coup_game.pending_action:
            action_player_id = coup_game.pending_action["player_id"]
            action = coup_game.pending_action["action"]

            # Execute the action
            result = coup_game._execute_action(action_player_id, action)

            # Close counteraction window and clear pending action
            coup_game.counteraction_window_open = False
            coup_game.pending_action = None

            return {
                "success": True,
                "message": "No one countered. Action succeeds.",
                "action_result": result,
            }

        return {"success": False, "message": "No pending action"}

    def complete_exchange(
        self, room_code: str, player_id: str, kept_indices: List[int]
    ) -> Dict:
        """Complete an exchange action"""
        coup_game = self.get_coup_game(room_code)
        if not coup_game:
            return {"success": False, "message": "Game not found"}

        return coup_game.complete_exchange(player_id, kept_indices)

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

        # Get the Coup game to check for pending actions
        coup_game = self.get_coup_game(room_code)
        pending_info = {}
        if coup_game:
            pending_info = {
                "challenge_window_open": coup_game.challenge_window_open,
                "counteraction_window_open": coup_game.counteraction_window_open,
                "pending_action": coup_game.pending_action,
                "pending_counteraction": coup_game.pending_counteraction,
            }

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
            **pending_info,
        }


# Create a singleton instance
manager = GameManager()
