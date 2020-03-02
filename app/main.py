import pymongo
import pymongo.errors
from datetime import datetime
from enum import Enum
from fastapi import FastAPI, Body, Depends, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from starlette import status
from starlette.responses import HTMLResponse
from typing import List


from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles

from app import crud
from app.database import client, users
from app.models import UserCreate, UserDBSecret, UserUpdate, User, PydanticObjectIdString
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
ME_SECOND_CHANCE = "app/main.py"
test_code = ""


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

RESPONSE_USERS_CONFIG = {
    "response_model_by_alias": False,
}


def check_presence(entity, entity_name="user"):
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity_name} not found"
        )


class DisplayParameters:
    def __init__(self, linenos: bool = False, style: StylesEnum = DEFAULT_STYLE):
        self.linenos = 'table' if linenos else linenos
        self.style = style.value if style != DEFAULT_STYLE else style


class ReadParameters:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


@app.exception_handler(pymongo.errors.DuplicateKeyError)
async def duplicate_key_error_handler(request: Request, exc: pymongo.errors.DuplicateKeyError):
    if "username" in exc.details['keyPattern'] or "email" in exc.details['keyPattern']:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "user already registered"}
        )


@app.on_event("startup")
async def db_startup():
    await users.create_index(
        [("username", pymongo.ASCENDING)],
        unique=True
    )


@app.on_event("startup")
def read_my_code():
    global ME
    global test_code

    try:
        with open(ME, "r") as f:
            test_code = f.read()
    except IOError:
        pass
    try:
        ME = ME_SECOND_CHANCE
        with open(ME, "r") as f:
            test_code = f.read()
    except IOError:
        test_code = 'print("Hello world!")'


@app.on_event("shutdown")
async def db_shutdown():
    await client.close()


async def style_parameter(style: StylesEnum = DEFAULT_STYLE):
    if style != DEFAULT_STYLE:
        style = style.value
    return style


@app.get("/test", response_class=HTMLResponse)
async def test(display: DisplayParameters = Depends()):
    """
    Return test
    """
    lexer = get_lexer_by_name("python")
    if test_code != 'print("Hello world!")':
        options = {'title': 'Snippets main.py code'}
    else:
        options = {'title': 'Python "Hello world!" example'}
    formatter = HtmlFormatter(linenos=display.linenos, style=display.style, full=True, **options)
    hl_code = highlight(test_code, lexer, formatter)
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
@app.get("/users/", response_model=List[User], **RESPONSE_USERS_CONFIG)
async def get_users(read_params: ReadParameters = Depends()):
    users = await crud.get_users(skip=read_params.skip, limit=read_params.limit)
    return users


@app.post("/users/", response_model=User, **RESPONSE_USERS_CONFIG)
async def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    created = datetime.utcnow()
    user_in_db = UserDBSecret(
        created=created,
        edited=created,
        hashed_password=hashed_password,
        **user.dict(exclude={'password'})
    )
    result = await crud.create_user(user_in_db.dict())

    new_user = user.dict()
    new_user.update({
        "_id": result.inserted_id,
        "created": created,
        "edited": created,
    })
    return new_user


@app.delete("/users/{user_id}")
async def get_user(user_id: PydanticObjectIdString = Path(...)):
    result = await crud.delete_user(user_id)
    check_presence(result.deleted_count)
    return {"message": "deleted"}


@app.get("/users/{user_id}", response_model=User, **RESPONSE_USERS_CONFIG)
async def get_user(user_id: PydanticObjectIdString = Path(...)):
    user = await crud.get_user(user_id)
    check_presence(user)
    return user


@app.patch("/users/{user_id}", response_model=User, **RESPONSE_USERS_CONFIG)
async def update_user(user_update: UserUpdate, user_id: PydanticObjectIdString = Path(...)):

    update_data = user_update.dict(exclude_unset=True)
    result = await crud.update_user(user_id, update_data)
    check_presence(result.matched_count)
    updated_user = await crud.get_user(user_id)

    return updated_user


