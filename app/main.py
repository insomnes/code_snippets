import pymongo.errors
from fastapi import FastAPI, Depends, HTTPException
from enum import Enum
from starlette import status
from starlette.responses import HTMLResponse
from typing import List

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles

import app.database as dbase
from app.models import User, UserCreate, UserInDBCreate
from app.security import get_password_hash

LEXERS = [lexer for lexer in get_all_lexers() if lexer[1]]
LANGUAGES = sorted([(lexer[1][0], lexer[0]) for lexer in LEXERS])
STYLES = sorted([style for style in get_all_styles()])
StylesEnum = Enum("StylesEnum", {s: s for s in STYLES})
DEFAULT_STYLE = "solarized-dark"

APP_TITLE = "Code snippets"
APP_DESCRIPTION = "Code snippets storage"
APP_VERSION = "0.1"

ME = "main.py"
my_code = ""

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)


class DisplayParameters:
    def __init__(self, linenos: bool = False, style: StylesEnum = DEFAULT_STYLE):
        self.linenos = 'table' if linenos else linenos
        self.style = style.value if style != DEFAULT_STYLE else style


class ReadParameters:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


@app.on_event("startup")
def read_my_code():
    global my_code
    with open(ME, "r") as f:
        my_code = f.read()


@app.on_event("startup")
async def dbase_unique_username_and_email():
    await dbase.db.users.create_index(
        "username", unique=True
    )
    await dbase.db.users.create_index(
        "email", unique=True
    )


@app.on_event("shutdown")
async def dbase_shutdown():
    await dbase.db.close()


async def style_parameter(style: StylesEnum = DEFAULT_STYLE):
    if style != DEFAULT_STYLE:
        style = style.value
    return style


@app.get("/myself", response_class=HTMLResponse)
async def myself(display: DisplayParameters = Depends()):
    """
    Return self code
    """
    lexer = get_lexer_by_name("python")
    options = {'title': 'Snippets main.py code'}
    formatter = HtmlFormatter(linenos=display.linenos, style=display.style, full=True, **options)
    hl_code = highlight(my_code, lexer, formatter)
    return hl_code


@app.get("/styles")
async def styles():
    """
    Return supported code highlighting styles
    """
    return {"styles": STYLES}


@app.get("/languages")
async def languages():
    """
    Return supported code programming languages
    """
    langs = {l[0]: l[1] for l in LANGUAGES}
    return {"languages": langs}


#################
# USERS SECTION #
#################
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    user_in_db = UserInDBCreate(**user.dict(), hashed_password=hashed_password)
    try:
        result = await dbase.create_user(user_in_db)
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )
    if not result.acknowledged:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user_info = User(_id=result.inserted_id, **user.dict())
    return user_info


@app.get("/users/", response_model=List[User])
async def get_users(read_params: ReadParameters = Depends()):
    users = await dbase.get_users(skip=read_params.skip, limit=read_params.limit)
    return users
