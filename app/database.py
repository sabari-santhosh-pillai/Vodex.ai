from motor.motor_asyncio import AsyncIOMotorClient
import os
from loguru import logger

# MongoDB connection string from environment variable
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")

# Create a MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Database
db = client["Vodex_ai"]

async def connect_to_mongo():
    try:
        # Ping the server to check the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    client.close()
    logger.info("Closed MongoDB connection")