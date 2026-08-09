from fastapi import FastAPI
from enum import Enum

from routers import day2, day3, day4, day5

app = FastAPI()

app.include_router(day2.router)
app.include_router(day3.router)
app.include_router(day4.router)
app.include_router(day5.router)

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

