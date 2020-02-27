from pydantic import BaseModel, EmailStr, Field
from typing import List


class MongoObjectID:

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return str(value)


class SnippetBase(BaseModel):
    title: str
    language: str


class Snippet(SnippetBase):
    code: str
    id: int
    owner_id: int


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_admin: bool = False
    is_active: bool = True

    snippets: List[Snippet] = None


class UserCreate(UserBase):
    password: str


class UserInDBCreate(UserBase):
    hashed_password: str


class UserInDB(UserInDBCreate):
    _id: MongoObjectID


class User(UserBase):
    _id: MongoObjectID

    class Config:
        orm_mode = True

