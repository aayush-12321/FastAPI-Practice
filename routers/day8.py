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



#! Server-Sent Events (SSE)

# You can stream data to the client using Server-Sent Events (SSE).

# This is similar to Stream JSON Lines, but uses the text/event-stream format, which is supported natively by browsers with the EventSource API.

# SSE is a standard for streaming data from the server to the client over HTTP.

# Each event is a small text block with "fields" like data, event, id, and retry, separated by blank lines.

# It looks like this:


# data: {"name": "Portal Gun", "price": 999.99}

# data: {"name": "Plumbus", "price": 32.99}
# SSE is commonly used for AI chat streaming, live notifications, logs and observability, and other cases where the server pushes updates to the client.


# To stream SSE with FastAPI, use yield in your path operation function and set response_class=EventSourceResponse.

#? Import EventSourceResponse from fastapi.sse:

from fastapi.sse import EventSourceResponse

@router.get("/items/stream-sse", response_class=EventSourceResponse)
async def sse_items() -> AsyncIterable[Item]:
    for item in items:
        yield item


class Item(BaseModel):
    name: str
    price: float


items = [
    Item(name="Plumbus", price=32.99),
    Item(name="Portal Gun", price=999.99),
    Item(name="Meeseeks Box", price=49.99),
]


# ServerSentEvent
# If you need to set SSE fields like event, id, retry, or comment, you can yield ServerSentEvent objects instead of plain data.

#? Import ServerSentEvent from fastapi.sse:

from fastapi.sse import ServerSentEvent

@router.get("/items/stream-sse1", response_class=EventSourceResponse)
async def stream_items() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(comment="stream of item updates")
    for i, item in enumerate(items):
        yield ServerSentEvent(data=item, event="item_update", id=str(i + 1), retry=5000)

# The data field is always encoded as JSON. You can pass any value that can be serialized as JSON, including Pydantic models.



# Raw Data
# If you need to send data without JSON encoding, use raw_data instead of data.

# This is useful for sending pre-formatted text, log lines, or special "sentinel" values like [DONE].

@router.get("/logs/stream", response_class=EventSourceResponse)
async def stream_logs() -> AsyncIterable[ServerSentEvent]:
    logs = [
        "2025-01-01 INFO  Application started",
        "2025-01-01 DEBUG Connected to database",
        "2025-01-01 WARN  High memory usage detected",
    ]
    for log_line in logs:
        yield ServerSentEvent(raw_data=log_line)

# Note: data and raw_data are mutually exclusive. You can only set one of them on each ServerSentEvent.



# Resuming with Last-Event-ID
# When a browser reconnects after a connection drop, it sends the last received id in the Last-Event-ID header.
# You can read it as a header parameter and use it to resume the stream from where the client left off:

from fastapi import Header
from typing import Annotated

class Item(BaseModel):
    name: str
    price: float


items = [
    Item(name="Plumbus", price=32.99),
    Item(name="Portal Gun", price=999.99),
    Item(name="Meeseeks Box", price=49.99),
]


@router.get("/items/stream-lei", response_class=EventSourceResponse)
async def stream_items(
    last_event_id: Annotated[int | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    start = last_event_id + 1 if last_event_id is not None else 0
    for i, item in enumerate(items):
        if i < start:
            continue
        yield ServerSentEvent(data=item, id=str(i))



# SSE with POST
# SSE works with any HTTP method, not just GET.

# This is useful for protocols like MCP that stream SSE over POST:


class Prompt(BaseModel):
    text: str


@router.post("/chat/stream", response_class=EventSourceResponse)
async def stream_chat(prompt: Prompt) -> AsyncIterable[ServerSentEvent]:
    words = prompt.text.split()
    for word in words:
        yield ServerSentEvent(data=word, event="token")
    yield ServerSentEvent(raw_data="[DONE]", event="done")



# Background Tasks

# First, import BackgroundTasks and define a parameter in your path operation function with a type declaration of BackgroundTasks:

from fastapi import BackgroundTasks

def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@router.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}

# FastAPI will create the object of type BackgroundTasks for you and pass it as that parameter.



# Dependency Injection
from fastapi import Depends

def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)


def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q


@router.post("/send-notification-de/{email}")
async def send_notification(
    email: str, background_tasks: BackgroundTasks, q: Annotated[str, Depends(get_query)]
):
    message = f"message to {email}\n"
    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}


#! Metadata and Docs URLs

#  Metadata for API
#? Written in main.py

# Create metadata for tags
# Let's try that in an example with tags for users and items.

# Create metadata for your tags and pass it to the openapi_tags parameter:

#? Written inside main.py


#?  Swagger UI: served at /docs.
# You can set its URL with the parameter docs_url.
# You can disable it by setting docs_url=None.

#? ReDoc: served at /redoc.
# You can set its URL with the parameter redoc_url.
# You can disable it by setting redoc_url=None.



#! Frontend

# You can serve static frontend apps with app.frontend() (or router.frontend()).


# Serve a Frontend

# After building your frontend, for example with npm run build, put the generated files in a directory, for example, dist.

# Your project structure could look like this:


# .
# ├── pyproject.toml
# ├── app
# │   ├── __init__.py
# │   └── main.py
# └── dist
#     ├── index.html
#     └── assets
#         └── app.js
# Then serve it with app.frontend():

# from fastapi import FastAPI

# app = FastAPI()

# app.frontend("/", directory="dist")

# With this, a request for /assets/app.js can serve dist/assets/app.js.

# If you also have a FastAPI path operation, the path operation wins


router.frontend("/", directory="dist", fallback="index.html")  

# Many frontend apps, including single-page apps (SPAs), use client-side routing. A path like /dashboard/settings might not be a real file but the framework would take care of handling it. So, if accessing that URL directly (instead of navigating through the app), the backend should serve the frontend app from index.html, so that the frontend framework can then handle the client-side routing.



# Custom 404 Page
# You can also serve a static 404.html page for missing frontend paths:


# Python 3.10+

# from fastapi import FastAPI

# app = FastAPI()

# app.frontend("/", directory="dist", fallback="404.html")

# That response keeps a status code of 404.

# In this case, FastAPI won't serve index.html for missing frontend paths. It will return the 404.html file instead.



# Fallback Auto

# By default, app.frontend() uses fallback="auto".

# If there is a 404.html file in the frontend directory, missing frontend paths serve that file with status code 404.

# Otherwise, if there is an index.html file, missing browser navigation paths serve index.html, which is what many frontend apps with client-side routing expect.

# So, in most cases you can use app.frontend("/", directory="dist") without specifying the fallback argument.

# from fastapi import FastAPI

# app = FastAPI()

# app.frontend("/", directory="dist")



# If you don't want to serve a fallback file for missing frontend paths, use fallback=None. Then missing frontend paths return the normal 404.



# Check Directory

# By default, app.frontend() uses check_dir="auto".

# When the FASTAPI_ENV environment variable is set to development, FastAPI only shows a warning if the frontend build output directory is missing. The fastapi dev command sets this environment variable for you if it is not already set. This lets you start the backend before building or starting the frontend during development.

# In any other environment, FastAPI raises an error when the app is created. This helps catch configuration errors early before deploying an app without its frontend files.

# You can also set check_dir=True to always check the directory when the app is created.

# If your frontend files are created later, for example by a separate build step after the app object is created, set check_dir=False:


# from fastapi import FastAPI

# app = FastAPI()

# app.frontend("/", directory="dist", check_dir=False)

# With check_dir=False, FastAPI will not check the directory when the app is created. If the configured directory is still missing when a request is handled, FastAPI will raise an error then.


# You can also add frontend files to an APIRouter and include it with a prefix:
#?router.frontend("/", directory="dist", fallback="index.html")




#! Static Files

# You can serve static files automatically from a directory using StaticFiles.

#? Tip: 

# If you need to host a frontend, use app.frontend() instead, read about it in Frontend.

# app.frontend() uses StaticFiles underneath, with several additional advantages for frontends, like handling client-side routing.


# Use StaticFiles

# Import StaticFiles.
# "Mount" a StaticFiles() instance in a specific path.

# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles

# app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")

#? This is different from using an APIRouter as a mounted application is completely independent. The OpenAPI and docs from your main application won't include anything from the mounted application, etc.


