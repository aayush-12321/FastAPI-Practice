from fastapi import FastAPI, Request
from enum import Enum
from fastapi.responses import JSONResponse

from routers import day2, day3, day4, day5
from routers.day5 import UnicornException

app = FastAPI()

app.include_router(day2.router)
app.include_router(day3.router)
app.include_router(day4.router)
app.include_router(day5.router)


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
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)


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

