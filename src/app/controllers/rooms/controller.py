from typing import Dict, List, Optional
import logging
from fastapi import WebSocket, WebSocketDisconnect

from app.controllers.websockets import manager as ws_manager
from app.controllers.websockets import process_message
from app.controllers.game import manager as game_manager
from app.controllers.rooms.utils import generate_room_code
from app.models.game import GameStatus

logger = logging.getLogger(__name__)


def create_room(room_code: str = None) -> str:
    """
    Create a new room with the given code or generate a new one.
    Returns the room code.
    """
    # Generate a unique room code if not provided
    if not room_code or room_code == "new":
        room_code = generate_room_code()

    # Check if room already exists in the connection manager
    if room_code in ws_manager.active_rooms:
        raise ValueError("Room already exists")

    return room_code


async def handle_room_connection(
    websocket: WebSocket, room_code: str, player_name: str, create: bool = False
) -> None:
    """
    Handle a new WebSocket connection to a room.
    This function encapsulates the entire connection lifecycle.
    """
    try:
        # If creating a new room, validate that the room code doesn't exist
        if create:
            try:
                room_code = create_room(room_code)
            except ValueError:
                await websocket.close(code=4000, reason="Room already exists")
                return

        # Connect to the room and get player ID
        player_id = await ws_manager.connect(websocket, room_code, player_name)

        # Send initial room state to the client
        players = [p["name"] for p in ws_manager.get_room_players(room_code)]
        await ws_manager.send_personal_message(
            websocket,
            {
                "type": "room_joined",
                "room_code": room_code,
                "players": players,
                "is_creator": create,
                "player_id": player_id,
            },
        )

        # Handle messages from this client
        try:
            while True:
                data = await websocket.receive_text()
                await process_message(websocket, data, room_code)
        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in websocket connection: {str(e)}")
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")


def handle_chat_message(
    websocket: WebSocket, room_code: str, message_text: str
) -> dict:
    """
    Handle a chat message from a client.
    Returns the message to broadcast.
    """
    player_name = None
    for player in ws_manager.get_room_players(room_code):
        if player["websocket"] == websocket:
            player_name = player["name"]
            break

    if player_name:
        return {
            "type": "chat",
            "player": player_name,
            "message": message_text,
        }

    return None


def handle_player_ready(websocket: WebSocket, room_code: str, is_ready: bool) -> dict:
    """
    Handle a player ready status change.
    Returns the message to broadcast.
    """
    ws_manager.set_player_ready(websocket, is_ready)

    # Get player name
    player_name = None
    for player in ws_manager.get_room_players(room_code):
        if player["websocket"] == websocket:
            player_name = player["name"]
            break

    return {"type": "player_ready", "player": player_name, "is_ready": is_ready}


def check_all_players_ready(room_code: str) -> bool:
    """
    Check if all players in a room are ready.
    If they are, start the game.
    Returns True if the game was started, False otherwise.
    """
    if not ws_manager.are_all_players_ready(room_code):
        return False

    # Get all players in the room with their IDs
    players = ws_manager.get_room_players(room_code)
    player_info = []
    for player in players:
        player_id = ws_manager.get_player_id(player["websocket"])
        player_info.append({"name": player["name"], "id": player_id})

    # Create a new game with the player IDs from the websocket manager
    game_manager.create_game(room_code, player_info)

    # Start the game
    game_manager.start_game(room_code)

    return True


def get_player_game_view(room_code: str, player_id: str) -> Optional[dict]:
    """
    Get the game state for a player.
    """
    return game_manager.get_player_view(room_code, player_id)
