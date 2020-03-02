from bson.objectid import ObjectId
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult
from typing import Any, Dict

from app.database import users_coll

DBData = Dict[str, Any]


# def mongo_id_serializer(method_with_user_id: Callable):
#     @wraps(method_with_user_id)
#     async def method_with_user_id_wrapper(user_id, *args, **kwargs):
#         if not isinstance(user_id, ObjectId):
#             user_id = ObjectId(str(user_id))
#
#         return await method_with_user_id(user_id, *args, **kwargs)
#     return method_with_user_id_wrapper
#


async def get_user(user_id: ObjectId):
    query = {
        '_id': user_id
    }
    return await users_coll.find_one(query)


async def create_user(user_data: DBData) -> InsertOneResult:
    return await users_coll.insert_one(user_data)


async def delete_user(user_id: ObjectId) -> DeleteResult:
    query = {
        '_id': user_id
    }
    return await users_coll.delete_one(query)


async def update_user(user_id: ObjectId, update_data: DBData) -> UpdateResult:
    query_filter = {"_id": user_id}
    query = {
        "$set": update_data,
        "$currentDate": {"edited": True}
    }

    return await users_coll.update_one(query_filter, query)


async def get_users(skip: int = 0, limit: int = 100):
    cursor = users_coll.find({}).skip(skip).limit(limit)
    return await cursor.to_list(limit)

