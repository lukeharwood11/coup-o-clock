from fastapi import (
    APIRouter,
    WebSocket,
    Query,
)
from app.controllers.rooms import controller as room_controller
import logging

router = APIRouter(tags=["WebSockets"])

logger = logging.getLogger(__name__)


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
    await room_controller.handle_room_connection(
        websocket, room_code, player_name, create
    )
