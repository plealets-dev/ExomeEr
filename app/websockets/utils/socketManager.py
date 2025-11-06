from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, event: str):
        print("websocket connection enabled")
        print(self.active_connections)
        if event not in self.active_connections:
            self.active_connections[event] = []
        self.active_connections[event].append(websocket)

    def disconnect(self, websocket: WebSocket, event: str):
        if event in self.active_connections:
            self.active_connections[event].remove(websocket)
    
    async def send_message(self, message: str, event: str):
        # Send message to all users in the event room
        if event in self.active_connections:
            for connection in self.active_connections[event]:
                await connection.send_text(message)

    async def broadcast(self, event: str, message: str):
        # Broadcast message to all users in the event
        await self.send_message(message, event)
