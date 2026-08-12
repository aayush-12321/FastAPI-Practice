from fastapi import APIRouter

router = APIRouter(prefix='/day8', tags=['Day 8'])

#! Bigger Applications - Multiple Files


#? Instead of adding all that(dependencies) to each path operation, we can add it to the APIRouter.

# from ..dependencies import get_token_header

# router = APIRouter(
#     prefix="/items",
#     tags=["items"],
#     dependencies=[Depends(get_token_header)],
#     responses={404: {"description": "Not found"}},
# )


##? Structure of a main.py

# from fastapi import Depends, FastAPI

# from .dependencies import get_query_token, get_token_header
# from .internal import admin
# from .routers import items, users

# app = FastAPI(dependencies=[Depends(get_query_token)])


# app.include_router(users.router)
# app.include_router(items.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


# @app.get("/")
# async def root():
#     return {"message": "Hello Bigger Applications!"}


## With app.include_router() we can add each APIRouter to the main FastAPI application.

# We can declare all these without having to modify the original APIRouter by passing those parameters to app.include_router():

# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


# As your FastAPI app object lives in app/main.py, you can configure the entrypoint in your pyproject.toml file like this:


# [tool.fastapi]
#? entrypoint = "app.main:app"
# that is equivalent to importing like:


# from app.main import app

# You could also pass the path to the command, like:

#?  uv run fastapi dev app/main.py



#! Stream JSON Lines

#? What is a Stream?
# "Streaming" data means that your app will start sending data items to the client without waiting for the entire sequence of items to be ready.

#? JSON Lines
# In these cases, it's common to send "JSON Lines", which is a format where you send one JSON object per line.

# {"name": "Plumbus", "description": "A multi-purpose household device."}
# {"name": "Portal Gun", "description": "A portal opening device."}
# {"name": "Meeseeks Box", "description": "A box that summons a Meeseeks."}

# It's very similar to a JSON array (equivalent of a Python list), but instead of being wrapped in [] and having , between the items, it has one JSON object per line, they are separated by a new line character.

# ecause each JSON object will be separated by a new line, they can't contain literal new line characters in their content, but they can contain escaped new lines (\n), which is part of the JSON standard.

# But normally you won't have to worry about it, it's done automatically.


#? Stream JSON Lines with FastAPI
# To stream JSON Lines with FastAPI you can, instead of using return in your path operation function, use yield to produce each item in turn.


from collections.abc import AsyncIterable, Iterable
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None


items = [
    Item(name="Plumbus", description="A multi-purpose household device."),
    Item(name="Portal Gun", description="A portal opening device."),
    Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
]


@router.get("/items/stream")
async def stream_items() -> AsyncIterable[Item]:
    for item in items:
        yield item


@router.get("/items/stream-no-async")
def stream_items_no_async() -> Iterable[Item]:
    for item in items:
        yield item


@router.get("/items/stream-no-annotation")
async def stream_items_no_annotation():
    for item in items:
        yield item


@router.get("/items/stream-no-async-no-annotation")
def stream_items_no_async_no_annotation():
    for item in items:
        yield item