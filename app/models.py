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


class Snippet(BaseModel):
    code: str
    code_language: LanguagesEnum
    created: datetime
    edited: datetime
    title: str = None
    description: str = None
    private: str = False

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    admin: bool = False
    inactive: bool = False


class UserCreate(UserBase):
    password: str


class UserDBBase(UserBase):
    created: datetime
    edited: datetime
    snippets: List[Snippet] = []


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
