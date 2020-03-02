from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import Collection

USER = "mongo"
PASSWORD = "mongo"
HOST = "localhost"
PORT = "27017"

URI = f"mongodb://{USER}:{PASSWORD}@{HOST}:{PORT}"

client = AsyncIOMotorClient(URI)
db = client.snippets
users_coll: Collection = db.users

