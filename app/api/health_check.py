from fastapi import APIRouter
# Initialize the router
health_check = APIRouter()

@health_check.get("/")
async def home():
    return True