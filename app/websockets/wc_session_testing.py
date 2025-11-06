from app.websockets.utils.socketManager import WebSocketManager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

manager = WebSocketManager()

wc_router = APIRouter()



@wc_router.websocket("/loadTest")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await asyncio.sleep(1)  # Simulate processing delay
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()



@wc_router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    
    await websocket.accept()
    # Wait for the initial user_data payload
    data = await websocket.receive_text()
    user_data = json.loads(data)
    username = user_data["username"]
    event = user_data["event"]
    print("event", event)
    # Connect the user
    await manager.connect(websocket, event)
    # await manager.connect(websocket, user_data.event)
    print("connection done")
    try:
        while True:
            # Receive a message from the client (JSON format)
            # data = await websocket.receive_text()
            # message = json.loads(data)
            # Handle message (you can process the message as needed)
            print(f"Received message from {username}: {user_data}")
            # Send message back to the event group
            await manager.broadcast(event, json.dumps({"message": user_data, "username": username}))
    except WebSocketDisconnect:
        manager.disconnect(websocket, event)
        print(f"{username} disconnected from {event}")