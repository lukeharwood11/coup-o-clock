import json
import logging
from fastapi import WebSocket
from typing import Dict, Any

from app.controllers.websockets import manager as ws_manager
from app.controllers.rooms import controller as room_controller
from app.controllers.game import manager as game_manager
from app.models.game import GameStatus

logger = logging.getLogger(__name__)


async def process_message(websocket: WebSocket, data: str, room_code: str) -> None:
    """Process a message from a client"""
    try:
        message = json.loads(data)
        message_type = message.get("type")
        player_id = ws_manager.get_player_id(websocket)

        if not player_id:
            await ws_manager.send_personal_message(
                websocket, {"type": "error", "message": "Player not found"}
            )
            return

        if message_type == "chat":
            # Handle chat messages
            if "message" in message:
                chat_message = room_controller.handle_chat_message(
                    websocket, room_code, message["message"]
                )
                if chat_message:
                    await ws_manager.broadcast_to_room(room_code, chat_message)

        elif message_type == "ready":
            # Handle player ready status
            is_ready = message.get("ready", False)
            ready_message = room_controller.handle_player_ready(
                websocket, room_code, is_ready
            )

            # Broadcast ready status to all players in the room
            await ws_manager.broadcast_to_room(room_code, ready_message)

            # Check if all players are ready to start the game
            if room_controller.check_all_players_ready(room_code):
                # Get all player names in the room
                player_names = [
                    p["name"] for p in ws_manager.get_room_players(room_code)
                ]

                # Send game start message to all players
                await ws_manager.broadcast_to_room(
                    room_code, {"type": "game_start", "players": player_names}
                )

                # Log debug information
                logger.info(
                    f"Game started in room {room_code} with players: {player_names}"
                )

                # Send initial game state to each player
                for player in ws_manager.get_room_players(room_code):
                    player_ws = player["websocket"]
                    player_id = ws_manager.get_player_id(player_ws)
                    if player_id:
                        player_view = room_controller.get_player_game_view(
                            room_code, player_id
                        )
                        logger.info(
                            f"Sending game state to player {player['name']} (ID: {player_id}): {player_view}"
                        )
                        await ws_manager.send_personal_message(
                            player_ws, {"type": "game_state", "state": player_view}
                        )

        elif message_type == "game_action":
            # Get the game state
            game_state = game_manager.get_game(room_code)
            if not game_state or game_state.status != GameStatus.PLAYING:
                await ws_manager.send_personal_message(
                    websocket, {"type": "error", "message": "Game not in progress"}
                )
                return

            # Process the game action based on the action type
            action = message.get("action", {})
            action_type = action.get("action_type")

            logger.info(f"Received game action: {action}")

            if not action_type:
                logger.error(f"No action type specified in action: {action}")
                await ws_manager.send_personal_message(
                    websocket, {"type": "error", "message": "No action type specified"}
                )
                return

            # Get player name for logging
            player_name = None
            for player in ws_manager.get_room_players(room_code):
                if player["websocket"] == websocket:
                    player_name = player["name"]
                    break

            # Process different action types
            result = None

            if action_type == "perform_action":
                # Player is performing a game action (income, foreign aid, coup, etc.)
                game_action = action.get("game_action", {})
                logger.info(f"Performing game action: {game_action}")
                result = game_manager.perform_action(room_code, player_id, game_action)

            elif action_type == "challenge":
                # Player is challenging an action
                result = game_manager.challenge_action(room_code, player_id)

            elif action_type == "pass_challenge":
                # Player is passing on challenging an action
                result = game_manager.pass_challenge(room_code, player_id)

            elif action_type == "counter":
                # Player is countering an action
                counter_action = action.get("counter_action", {})
                result = game_manager.counter_action(
                    room_code, player_id, counter_action
                )

            elif action_type == "pass_counter":
                # Player is passing on countering an action
                result = game_manager.pass_counter(room_code, player_id)

            elif action_type == "complete_exchange":
                # Player is completing an exchange action
                kept_indices = action.get("kept_indices", [])
                result = game_manager.complete_exchange(
                    room_code, player_id, kept_indices
                )

            else:
                await ws_manager.send_personal_message(
                    websocket,
                    {"type": "error", "message": f"Unknown action type: {action_type}"},
                )
                return

            if not result:
                await ws_manager.send_personal_message(
                    websocket, {"type": "error", "message": "Failed to process action"}
                )
                return

            # Broadcast the action result to all players
            await ws_manager.broadcast_to_room(
                room_code,
                {
                    "type": "game_action_result",
                    "action_type": action_type,
                    "result": result,
                    "player": player_name or "Unknown",
                },
            )

            # Check if the game is over
            if result.get("game_over", False):
                # Find the winner
                winner = None
                for player in game_state.players:
                    if player.is_alive:
                        winner = player.name
                        break

                # Send game over message
                await ws_manager.broadcast_to_room(
                    room_code,
                    {
                        "type": "game_over",
                        "winner": winner,
                    },
                )

            # Update game state for all players
            for player in ws_manager.get_room_players(room_code):
                player_ws = player["websocket"]
                player_id = ws_manager.get_player_id(player_ws)
                if player_id:
                    player_view = room_controller.get_player_game_view(
                        room_code, player_id
                    )
                    await ws_manager.send_personal_message(
                        player_ws, {"type": "game_state", "state": player_view}
                    )

    except json.JSONDecodeError:
        await ws_manager.send_personal_message(
            websocket, {"type": "error", "message": "Invalid JSON message"}
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await ws_manager.send_personal_message(
            websocket,
            {"type": "error", "message": f"Error processing message: {str(e)}"},
        )
