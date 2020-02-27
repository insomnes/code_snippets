from fastapi.logger import logger

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from app.models import UserInDB, User, UserInDBCreate


MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_USER = ""
MONGODB_PASS = ""

if MONGODB_USER and MONGODB_PASS:
    MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}"
else:
    MONGODB_URI = f"mongodb://{MONGODB_HOST}:{MONGODB_PORT}"

client = AsyncIOMotorClient(MONGODB_URI)
db = client.snippets_database


async def create_user(user: UserInDBCreate):
    result = await db.users.insert_one(user.dict())
    logger.info(f"Created user {user.username} with id {result.inserted_id}")
    return result


async def get_user(user_id: str):
    user_id = ObjectId(user_id)
    query = {'_id': user_id}
    user = await db.users.find_one(query)

    return user


async def get_users(skip: int = 0, limit: int = 100):
    query = dict()
    cursor = db.users.find(query).skip(skip).limit(limit)

    return await cursor.to_list(length=limit)
