import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if MONGO_URI is set
if not os.getenv("MONGO_URI"):
    raise ValueError("MONGO_URI environment variable is not set")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import items, clock_in
from loguru import logger
from database import connect_to_mongo, close_mongo_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up the application")
    await connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down the application")
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(items.router, prefix="/api/v1")
app.include_router(clock_in.router, prefix="/api/v1/clock-in")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)