from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request, status
from pydantic import BaseModel
from typing import Annotated
from fastapi.responses import HTMLResponse, JSONResponse

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


