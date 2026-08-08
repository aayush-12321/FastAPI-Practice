from fastapi import FastAPI, APIRouter, Cookie, Header
from typing import Annotated, Any
from pydantic import BaseModel, EmailStr


router = APIRouter(prefix='/day-4', tags=['Day 4'])



#! Cookie Parameters

@router.get('/item')
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    '''
    Cookie parameters are used to capture the value of ads_id from the cookie.
    '''
    return {"ads_id": ads_id}


#! Header Parameters

@router.get("/items-header/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    '''
    Header parameters are used to capture the value of user_agent from the header.
    '''

    return {"User-Agent": user_agent}


## it converts - to _ in the header name to match the parameter name. For example, if the header name is User-Agent, it will be converted to user_agent. If you want to disable this behavior, you can set convert_underscores=False in the Header() function.
@router.get("/item-header-convert/")
async def read_items(
    strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
):

    '''
    it converts - to _ in the header name to match the parameter name. For example, if the header name is User-Agent, it will be converted to user_agent. If you want to disable this behavior, you can set convert_underscores=False in the Header() function.

    '''
    return {"strange_header": strange_header}


## Duplicate Header Parameters

@router.get("/item-header-duplicate/")
async def read_items(x_token: Annotated[list[str] | None, Header()] = None):
    '''
    It is possible to receive duplicate headers. That means, the same header with multiple values.

    You can define those cases using a list in the type declaration.

    You will receive all the values from the duplicate header as a Python list.

    For example, to declare a header of X-Token that can appear more than once, you can write:

    '''
    return {"X-Token values": x_token}



#! Cookie Parameters Model

class Cookies(BaseModel):
    model_config = {"extra": "forbid"}  # If a client tries to send some extra cookies, they will receive an error response.


    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@router.get("/items-cookie-params-model/")
async def read_items_cpm(cookies: Annotated[Cookies, Cookie()]):
    '''
    This endpoint demonstrates the use of a Pydantic model to define and validate cookie parameters.
    '''
    return cookies



#! Header Parameter Models

class CommonHeaders(BaseModel):
    model_config = {"extra": "forbid"}  # If a client tries to send some extra headers, they will receive an error response.

    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@router.get("/items-header-pm/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
# async def read_items(headers: Annotated[CommonHeaders, Header(convert_underscores=False)]):  # if you have a header parameter save_data in the code, the expected HTTP header will be save-data, and it will show up like that in the docs.
    '''
    Header Parameter Models
    '''
    return headers



#! Response Model - Return Type

# You can declare the type used for the response by annotating the path operation function return type.
# You can use type annotations the same way you would for input data in function parameters, you can use Pydantic models, lists, dictionaries, scalar values like integers, booleans, etc.

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@router.post("/items-rt/")
async def create_item(item: Item) -> Item:
    return item


@router.get("/items-rt1/")
async def read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),]


## response_model Parameter

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@router.post("/items-rm/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@router.get("/items-rm1/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]


## Return different o/p data than i/p data

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@router.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    '''
    In this case, because the two models are different, if we annotated the function return type as UserOut, the editor and tools would complain that we are returning an invalid type, as those are different classes.
    '''
    return user


## IF we follow this approach, we can return the same object, but FastAPI will filter the output to match the response model. This is useful when you want to hide certain fields from the response, such as passwords or sensitive information. And we dont need to include response_model in the decorator, as we have already specified the return type in the function signature. FastAPI will use that to generate the OpenAPI schema and documentation.
## we get tooling support, from editors and mypy as this code is correct in terms of types, but we also get the data filtering from FastAPI.

class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


@router.post("/user1/")
async def create_user(user: UserIn) -> BaseUser:
    return user


## Other Return Type Annotations

# There might be cases where you return something that is not a valid Pydantic field and you annotate it in the function, only to get the support provided by tooling (the editor, mypy, etc).

from fastapi import Response
from fastapi.responses import JSONResponse, RedirectResponse

@router.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})



# But when you return some other arbitrary object that is not a valid Pydantic type (e.g. a database object) and you annotate it like that in the function, FastAPI will try to create a Pydantic response model from that type annotation, and will fail.

# The same would happen if you had something like a union between different types where one or more of them are not valid Pydantic types, for example this would fail 💥

# This fails because the type annotation is not a Pydantic type and is not just a single Response class or subclass, it's a union (any of the two) between a Response and a dict.


# @router.get("/portal-fail")
# async def get_portal(teleport: bool = False) -> Response | dict:
#     if teleport:
#         return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
#     return {"message": "Here's your interdimensional portal."}




# Continuing from the example above, you might not want to have the default data validation, documentation, filtering, etc. that is performed by FastAPI.

# But you might want to still keep the return type annotation in the function to get the support from tools like editors and type checkers (e.g. mypy).

# In this case, you can disable the response model generation by setting response_model=None

# This will make FastAPI skip the response model generation and that way you can have any return type annotations you need without it affecting your FastAPI application. 🤓


@router.get("/portal-work", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}




# Your response model could have default values.

# but you might want to omit them from the result if they were not actually stored.

# For example, if you have models with many optional attributes in a NoSQL database, but you don't want to send very long JSON responses full of default values.

# Use the response_model_exclude_unset parameter¶
# You can set the path operation decorator parameter response_model_exclude_unset=True

# and those default values won't be included in the response, only the values actually set.


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@router.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]