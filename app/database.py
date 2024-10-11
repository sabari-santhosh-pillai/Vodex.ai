from motor.motor_asyncio import AsyncIOMotorClient
import os

# MongoDB connection string from environment variable
MONGO_URI = os.getenv("MONGO_URI")

# Create a MongoDB client
client = AsyncIOMotorClient(MONGO_URI)

# Database
db = client["Vodex_ai"]
