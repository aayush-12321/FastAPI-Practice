from fastapi import FastAPI, Request
from enum import Enum
from fastapi.responses import JSONResponse

from routers import day2, day3, day4, day5, day6, day7, day8, day8_part2
from routers.day5 import UnicornException


#! Day 8

# Metadata for tags users and items
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

# Metadata for API
description = """
Practicing FastPI. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

app = FastAPI(
    title="FastAPI Practice",
    description=description,
    summary="Practicing FastAPI from it's Oficial Documentation",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Aayush Parajuli",
        "url": "https://parajuliaayush.com.np",
        "email": "aayushparajuli23@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        # "identifier": "Apache-2.0", # Since OpenAPI 3.1.0 and FastAPI 0.99.0, you can also set the license_info with an identifier instead of a url.

    },

    tags_metadata = tags_metadata,   # Metadata for the tags

    # Docs URL Config
    # docs_url= '/mydocs',
    # redoc_url=None,
)

app.include_router(day2.router)
app.include_router(day3.router)
app.include_router(day4.router)
app.include_router(day5.router)
app.include_router(day6.router)
app.include_router(day7.router)
app.include_router(day8.router)
app.include_router(day8_part2.router)


#! DAY 5  ####################################33

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)


#! ##################################################



#! Day 7 ############################################

# Middleware

import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# CORS (Cross-Origin Resource Sharing)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#! SQl Databases

from routers.day7 import create_db_and_tables

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#! ##################################################



#! Day 8 ############################################

@app.get("/demo/")
async def read_items():
    return [{"name": "Katana"}]


# Metadata for Tags 

@app.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]


@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]
#! ##################################################



@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"



#! PATH PARAMETERS

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    '''
    Path parameter is used to capture the value of user_id from the URL.
    '''
    return {"user_id": user_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    '''
    Get model information based on the model name.
    '''
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/file/{file_path:path}")
async def read_file(file_path:str):
    '''
    :path is used to capture the entire path after /file/ in the URL.
    '''

    return {"file_path": file_path}

