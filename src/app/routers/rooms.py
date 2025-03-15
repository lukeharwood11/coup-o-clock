from app.controllers.rooms import utils as room_utils
from fastapi import APIRouter, HTTPException
from botocore.exceptions import ClientError
from decimal import Decimal
from app.models import Room
from typing import List
import boto3

router = APIRouter(prefix="/rooms", tags=["Rooms"])

dynamodb = boto3.resource(
    "dynamodb", region_name="us-east-2", endpoint_url="http://localhost:8000"
)
table = dynamodb.Table("Rooms")


@router.post("", response_model=Room)
async def create_room(room: Room):
    """
    Create a new room with a generated unique code
    """
    # Generate a unique room code
    room.code = room_utils.generate_room_code()

    # Convert the room model to a dictionary for DynamoDB
    room_item = {
        "code": room.code,
        "variation": room.variation,
        "room_price": str(room.room_price),  # Convert Decimal to string for DynamoDB
        "room_settings": room.room_settings.model_dump(),
    }

    try:
        # Put the item in the DynamoDB table
        table.put_item(Item=room_item)
        return room
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@router.get("", response_model=List[Room])
async def list_rooms():
    """
    List all rooms
    """
    try:
        response = table.scan()
        rooms = response.get("Items", [])

        # Convert DynamoDB items to Room models
        result = []
        for item in rooms:
            # Convert string back to Decimal for room_price
            room_price = Decimal(item.get("room_price"))

            # Create Room object
            room = Room(
                code=item.get("code"),
                variation=item.get("variation"),
                room_price=room_price,
                room_settings=item.get("room_settings"),
            )
            result.append(room)

        return result
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to list rooms: {str(e)}")


@router.get("/{room_code}", response_model=Room)
async def get_room(room_code: str):
    """
    Get a specific room by its code
    """
    try:
        response = table.get_item(Key={"code": room_code})
        item = response.get("Item")

        if not item:
            raise HTTPException(
                status_code=404, detail=f"Room with code {room_code} not found"
            )

        # Convert string back to Decimal for room_price
        room_price = Decimal(item.get("room_price"))

        # Create Room object
        room = Room(
            code=item.get("code"),
            variation=item.get("variation"),
            room_price=room_price,
            room_settings=item.get("room_settings"),
        )

        return room
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to get room: {str(e)}")


@router.put("/{room_code}", response_model=Room)
async def update_room(room_code: str, room: Room):
    """
    Update a room by its code
    """
    # Ensure the room code in the path matches the one in the request body
    if room.code and room.code != room_code:
        raise HTTPException(
            status_code=400, detail="Room code in path does not match room code in body"
        )

    # Set the room code from the path
    room.code = room_code

    # Convert the room model to a dictionary for DynamoDB
    room_item = {
        "code": room.code,
        "variation": room.variation,
        "room_price": str(room.room_price),  # Convert Decimal to string for DynamoDB
        "room_settings": room.room_settings.dict(),
    }

    try:
        # Check if the room exists
        response = table.get_item(Key={"code": room_code})
        if not response.get("Item"):
            raise HTTPException(
                status_code=404, detail=f"Room with code {room_code} not found"
            )

        # Update the item in the DynamoDB table
        table.put_item(Item=room_item)
        return room
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to update room: {str(e)}")


@router.delete("/{room_code}", response_model=dict)
async def delete_room(room_code: str):
    """
    Delete a room by its code
    """
    try:
        # Check if the room exists
        response = table.get_item(Key={"code": room_code})
        if not response.get("Item"):
            raise HTTPException(
                status_code=404, detail=f"Room with code {room_code} not found"
            )

        # Delete the item from the DynamoDB table
        table.delete_item(Key={"code": room_code})

        return {"message": f"Room with code {room_code} deleted successfully"}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete room: {str(e)}")
