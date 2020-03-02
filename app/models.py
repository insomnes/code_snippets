import re
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from pydantic.errors import PydanticValueError
from pygments.lexers import get_all_lexers
from typing import List
from bson.objectid import ObjectId as BsonObjectId
from bson.errors import InvalidId


OBJECTID_STRING_RE = r"^([a-f]|[0-9]){24}$"


class ObjectIDValueError(PydanticValueError):
    msg_template = "value is not valid ID"


class PydanticObjectId(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return str(v)


class PydanticObjectIdString(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return BsonObjectId(v)
        except InvalidId:
            raise ObjectIDValueError()


############
# SNIPPETS #
############
LANGUAGES = [lexer[1][0] for lexer in get_all_lexers() if lexer[1]]
LanguagesEnum = Enum("LanguagesEnum", {s: s for s in LANGUAGES})
SNIPPET_DEFAULT_TITLE = "Code snippet"


class SnippetBase(BaseModel):
    title: str = SNIPPET_DEFAULT_TITLE
    description: str = None
    code: str
    code_language: LanguagesEnum = None


class SnippetCreate(SnippetBase):
    pass


class SnippetDB(SnippetBase):
    id: PydanticObjectId = Field(..., alias="_id")
    owner_id: PydanticObjectId = Field(..., alias="_id")
    owner_username: str
    created: datetime
    last_modified: datetime


class Snippet(SnippetDB):
    class Config:
        orm_mode = True


#########
# USERS #
#########
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserDBBase(UserBase):
    created: datetime
    edited: datetime
    snippets_ids: List[str] = []


class UserDBSecret(UserDBBase):
    hashed_password: str


class User(UserDBBase):
    id: PydanticObjectId = Field(..., alias="_id")

    class Config:
        orm_mode = True


class UserSecret(UserDBSecret, User):
    pass


class UserUpdate(UserBase):
    username: str = None
    email: str = None
