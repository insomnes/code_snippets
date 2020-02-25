from enum import Enum
from pydantic import BaseModel
from pygments.lexers import get_all_lexers


PYGMENTS_LEXERS = [lexer for lexer in get_all_lexers() if lexer[1]]
PygmentsLexersEnum = Enum("PygmentsLexersEnum", {l: l for l in PYGMENTS_LEXERS})


class SnippetBase(BaseModel):
    title: str
    language: str


class Snippet(SnippetBase):
    code: str
    id: int
    owner_id: int


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    admin: bool

    class Config:
        orm_mode = True
