from typing import Dict, List, Set, Optional
from fastapi import WebSocket
import json
import uuid


class ConnectionManager:
    def __init__(self):
        # Map of room_code -> set of websocket connections
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        # Map of websocket -> room_code
        self.connection_rooms: Dict[WebSocket, str] = {}
        # Map of room_code -> list of player information
        self.room_players: Dict[str, List[Dict]] = {}
        # Map of websocket -> player_id
        self.player_ids: Dict[WebSocket, str] = {}

    async def connect(
        self, websocket: WebSocket, room_code: str, player_name: str
    ) -> str:
        """Connect a websocket to a room and return the player ID"""
        await websocket.accept()

        # Generate a unique player ID
        player_id = str(uuid.uuid4())
        self.player_ids[websocket] = player_id

        # Create room if it doesn't exist
        if room_code not in self.active_rooms:
            self.active_rooms[room_code] = set()
            self.room_players[room_code] = []

        # Add connection to room
        self.active_rooms[room_code].add(websocket)
        self.connection_rooms[websocket] = room_code

        # Add player to room
        player_info = {"name": player_name, "websocket": websocket, "is_ready": False}
        self.room_players[room_code].append(player_info)

        # Notify all clients in the room about the new player
        await self.broadcast_to_room(
            room_code,
            {
                "type": "player_joined",
                "player_name": player_name,
                "players": [p["name"] for p in self.room_players[room_code]],
            },
        )

        return player_id

    async def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket from its room"""
        if websocket not in self.connection_rooms:
            return

        room_code = self.connection_rooms[websocket]

        # Remove player from room_players
        player_name = None
        for i, player in enumerate(self.room_players[room_code]):
            if player["websocket"] == websocket:
                player_name = player["name"]
                self.room_players[room_code].pop(i)
                break

        # Remove connection from room
        self.active_rooms[room_code].remove(websocket)
        del self.connection_rooms[websocket]

        # Remove player ID
        if websocket in self.player_ids:
            del self.player_ids[websocket]

        # If room is empty, remove it
        if not self.active_rooms[room_code]:
            del self.active_rooms[room_code]
            del self.room_players[room_code]
        else:
            # Notify remaining clients about the player leaving
            await self.broadcast_to_room(
                room_code,
                {
                    "type": "player_left",
                    "player_name": player_name,
                    "players": [p["name"] for p in self.room_players[room_code]],
                },
            )

    async def broadcast_to_room(self, room_code: str, message: dict):
        """Send a message to all connections in a room"""
        if room_code not in self.active_rooms:
            return

        for connection in self.active_rooms[room_code]:
            await connection.send_text(json.dumps(message))

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific connection"""
        await websocket.send_text(json.dumps(message))

    def get_room_players(self, room_code: str) -> List[Dict]:
        """Get all players in a room"""
        return self.room_players.get(room_code, [])

    def get_player_id(self, websocket: WebSocket) -> Optional[str]:
        """Get the player ID for a websocket"""
        return self.player_ids.get(websocket)

    def set_player_ready(self, websocket: WebSocket, is_ready: bool):
        """Set a player's ready status"""
        if websocket not in self.connection_rooms:
            return False

        room_code = self.connection_rooms[websocket]

        for player in self.room_players[room_code]:
            if player["websocket"] == websocket:
                player["is_ready"] = is_ready
                return True

        return False

    def are_all_players_ready(self, room_code: str) -> bool:
        """Check if all players in a room are ready"""
        if room_code not in self.room_players:
            return False

        return all(player["is_ready"] for player in self.room_players[room_code])


# Create a singleton instance
manager = ConnectionManager()
