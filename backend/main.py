import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DB = os.getenv("MONGO_DB", "testDB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "testCollection")

# Encode password for URI
encoded_password = quote_plus(MONGO_PASSWORD)
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{encoded_password}@cluster0.pgaez3d.mongodb.net/?appName=Cluster0"

# Async MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# FastAPI app
app = FastAPI(title="Async FastAPI MongoDB Example")

# Pydantic model
class User(BaseModel):
    name: str
    age: int

# Create user
@app.post("/users")
async def create_user(user: User):
    result = await collection.insert_one(user.dict())
    return {"id": str(result.inserted_id)}

# Get all users
@app.get("/users")
async def get_users():
    users = []
    async for user in collection.find():
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

# Get user by ID
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Delete user by ID
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        return {"status": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")
