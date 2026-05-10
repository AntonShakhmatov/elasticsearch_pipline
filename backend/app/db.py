import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://root:test@mongo:27017/")

client = AsyncIOMotorClient(MONGO_URL)

db = client.osint_platform
pages_collection = db.pages