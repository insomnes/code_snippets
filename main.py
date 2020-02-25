from fastapi import FastAPI, Depends
from starlette.responses import HTMLResponse

from enum import Enum

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_all_styles


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


@app.on_event("startup")
def read_my_code():
    global my_code
    with open(ME, "r") as f:
        my_code = f.read()


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
