from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Query,
)
from app.controllers.websockets import manager as ws_manager
from app.controllers.game import manager as game_manager
from app.controllers.rooms import utils as room_utils
from app.models.game import GameStatus
from typing import Dict
import logging
import json
import uuid

router = APIRouter(tags=["WebSockets"])

logger = logging.getLogger(__name__)

# Map of websocket -> player_id
player_ids: Dict[WebSocket, str] = {}


@router.websocket("/ws/room/{room_code}")
async def websocket_room_endpoint(
    websocket: WebSocket,
    room_code: str,
    player_name: str = Query(...),
    create: bool = Query(False),
):
    """
    WebSocket endpoint for connecting to a room.
    If create=True, a new room will be created with the given code.
    Otherwise, the player will join an existing room.
    """
    try:
        # Generate a unique player ID
        player_id = str(uuid.uuid4())
        player_ids[websocket] = player_id

        # If creating a new room, validate that the room code doesn't exist
        if create:
            # Generate a unique room code if not provided
            if not room_code or room_code == "new":
                room_code = room_utils.generate_room_code()

            # Check if room already exists in the connection manager
            if room_code in ws_manager.active_rooms:
                await websocket.close(code=4000, reason="Room already exists")
                return

        # Connect to the room
        await ws_manager.connect(websocket, room_code, player_name)

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
                await process_message(websocket, data, room_code, player_id)
        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)
            if websocket in player_ids:
                del player_ids[websocket]
    except Exception as e:
        logger.error(f"Error in websocket connection: {str(e)}")
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")


async def process_message(
    websocket: WebSocket, data: str, room_code: str, player_id: str
):
    """Process a message from a client"""
    try:
        message = json.loads(data)
        message_type = message.get("type")

        if message_type == "chat":
            # Handle chat messages
            player_name = None
            for player in ws_manager.get_room_players(room_code):
                if player["websocket"] == websocket:
                    player_name = player["name"]
                    break

            if player_name and "message" in message:
                await ws_manager.broadcast_to_room(
                    room_code,
                    {
                        "type": "chat",
                        "player": player_name,
                        "message": message["message"],
                    },
                )

        elif message_type == "ready":
            # Handle player ready status
            is_ready = message.get("ready", False)
            ws_manager.set_player_ready(websocket, is_ready)

            # Get player name
            player_name = None
            for player in ws_manager.get_room_players(room_code):
                if player["websocket"] == websocket:
                    player_name = player["name"]
                    break

            # Broadcast ready status to all players in the room
            await ws_manager.broadcast_to_room(
                room_code,
                {"type": "player_ready", "player": player_name, "is_ready": is_ready},
            )

            # Check if all players are ready to start the game
            if ws_manager.are_all_players_ready(room_code):
                # Get all player names in the room
                player_names = [
                    p["name"] for p in ws_manager.get_room_players(room_code)
                ]

                # Create a new game
                game_state = game_manager.create_game(room_code, player_names)

                # Start the game
                game_state = game_manager.start_game(room_code)

                # Send game start message to all players
                await ws_manager.broadcast_to_room(
                    room_code, {"type": "game_start", "players": player_names}
                )

                # Send initial game state to each player
                for player in ws_manager.get_room_players(room_code):
                    player_ws = player["websocket"]
                    player_id = player_ids.get(player_ws)
                    if player_id:
                        player_view = game_manager.get_player_view(room_code, player_id)
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

            # Process the game action (to be implemented based on game rules)
            # For now, just echo the action to all players
            player_name = None
            for player in ws_manager.get_room_players(room_code):
                if player["websocket"] == websocket:
                    player_name = player["name"]
                    break

            await ws_manager.broadcast_to_room(
                room_code,
                {
                    "type": "game_action",
                    "action": message.get("action", {}),
                    "player": player_name or "Unknown",
                },
            )

            # Update game state for all players
            for player in ws_manager.get_room_players(room_code):
                player_ws = player["websocket"]
                player_id = player_ids.get(player_ws)
                if player_id:
                    player_view = game_manager.get_player_view(room_code, player_id)
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
