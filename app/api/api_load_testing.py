from fastapi import FastAPI, WebSocket, APIRouter
import time
import asyncio

api_test_router = APIRouter()




@api_test_router.get("/load-test")
async def load_test(duration: int = 1):
    """Simulates workload by sleeping for the given duration (in seconds)."""
    time.sleep(duration)
    return {"message": f"Processed workload for {duration} seconds"}