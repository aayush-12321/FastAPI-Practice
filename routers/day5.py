from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request, status, Depends
from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix='/day5', tags=['Day 5'])


#! Request Files

# To receive uploaded files, first install python-multipart.

# uv add python-multipart


@router.post('/files')
async def create_file(
            file: Annotated[bytes, File(description='A file read as bytes.')]
            # file: Annotated[bytes, File()]
    ):
    return {'file_size': len(file)}


@router.post('/uploadfile')
async def create_file(
            file: Annotated[UploadFile, File(description= 'A file read as UploadFile')]  #Y ou can also use File() with UploadFile, for example, to set additional metadata
           
            # file: UploadFile
    ):
    return {'file_name': file.filename}


## Upload Multiple Files

@router.post("/files-multi/")
async def create_files(
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}


@router.post("/uploadfiles-multi/")
async def create_upload_files(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    return {"filenames": [file.filename for file in files]}


@router.get("/files-multi")
async def main():
    content = """
<body>
<form action="/files-multi/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles-multi/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


#! Request forms and files


@router.post("/files-forms/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }



#! Handling Errors


items = {"foo": "The Foo Wrestlers"}

@router.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")  # When raising an HTTPException, you can pass any value that can be converted to JSON as the parameter detail, not only str. You could pass a dict, a list, etc. They are handled automatically by FastAPI and converted to JSON.
    return {"item": items[item_id]}


## Add custom headers

@router.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    '''
    There are some situations where it's useful to be able to add custom headers to the HTTP error. For example, for some types of security.

    You probably won't need to use it directly in your code.

    But in case you needed it for an advanced scenario, you can add custom headers:
    '''

    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}



## Install custom exception handlers


# You can add custom exception handlers with the same exception utilities from Starlette.

# Let's say you have a custom exception UnicornException that you (or a library you use) might raise.

# And you want to handle this exception globally with FastAPI.

# You could add a custom exception handler with @app.exception_handler()


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


# API Router doesn't support exception_handler so the exception handler function is defined in main using app(FastAPI())


@router.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}



## Override the HTTPException error handler

#### Code included in main.py as it requires app(FastAPI())

@router.get("/items-custom/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}




#! Path Operation Configuration

# There are several parameters that you can pass to your path operation decorator to configure it.

## Response Status Code
# You can define the (HTTP) status_code to be used in the response of your path operation.

# You can pass directly the int code, like 404.

# But if you don't remember what each number code is for, you can use the shortcut constants in status

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@router.post("/items-path-opr-config/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Item:
    return item


## Tags

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


# @router.post("/items/", tags=["items"])
# async def create_item(item: Item) -> Item:
#     return item


# @router.get("/items/", tags=["items"])
# async def read_items():
#     return [{"name": "Foo", "price": 42}]


# @router.get("/users/", tags=["users"])
# async def read_users():
#     return [{"username": "johndoe"}]



## Tags with Enums

from enum import Enum

class Tags(Enum):
    items = "items"
    users = "users"


# @router.get("/items/", tags=[Tags.items])
# async def get_items():
#     return ["Portal gun", "Plumbus"]


# @router.get("/users/", tags=[Tags.users])
# async def read_users():
#     return ["Rick", "Morty"]



## Summary and Description

@router.post(
    "/items/",
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
async def create_item(item: Item) -> Item:
    return item


## Description from docstring

@router.post(
    "/items-doc-string/",
    summary="Create an item",
    response_description="The created item",  # OpenAPI specifies that each path operation requires a response description. So, if you don't provide one, FastAPI will automatically generate one of "Successful response".
    deprecated= True # If you need to mark a path operation as deprecated, but without removing it, pass the parameter deprecated:


)
async def create_item(item: Item) -> Item:
    '''
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    '''
    return item



#! JSON Compatible Encoder


# There are some cases where you might need to convert a data type (like a Pydantic model) to something compatible with JSON (like a dict, list, etc).

# For example, if you need to store it in a database.

# For that, FastAPI provides a jsonable_encoder() function.

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


@router.put("/items-encode/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return fake_db



#! Body - Updates


## Update replacing with PUT

class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@router.get("/items-up/", response_model=None)
async def read_item() -> dict:
    return items

# @router.get("/items-up/", response_model=list[Item])
# async def read_item():
#     return list(items.values())


@router.put("/items-up/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded




#! Dependencies


# "Dependency Injection" means, in programming, that there is a way for your code (in this case, your path operation functions) to declare things that it requires to work and use: "dependencies".

# And then, that system (in this case FastAPI) will take care of doing whatever is needed to provide your code with those needed dependencies ("inject" the dependencies).

# This is very useful when you need to:

# Have shared logic (the same code logic again and again).
# Share database connections.
# Enforce security, authentication, role requirements, etc.
# And many other things...
# All these, while minimizing code repetition.

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


# @router.get("/items-depends/")
# async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
#     return commons


# @router.get("/users-depends/")
# async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
#     return commons


CommonsDep = Annotated[dict, Depends(common_parameters)]  # This is just standard Python, it's called a "type alias", it's actually not specific to FastAPI.




@router.get("/items/-depends")
async def read_items(commons: CommonsDep):
    return commons


@router.get("/users/-depends/")
async def read_users(commons: CommonsDep):
    return commons


