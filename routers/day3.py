from fastapi import Body, FastAPI, APIRouter, Path, Query
from typing import Annotated, Literal
from pydantic import BaseModel, Field

router = APIRouter(prefix="/day-3", tags=["Day 3"])


#! Path Parameters and Numeric Validations


## Path params validation

@router.get("/items/{item_id}")
async def read_items(
                item_id: Annotated[str, Path(title= "The id of an item to get")],
                q: str
                    ):

    '''
    Path parameters validation is used to validate the value of item_id from the URL.
    '''
    results = {'item_id': item_id}

    if q:
        results.update({"q": q})

    return results


## Numeric Validations

@router.get("/items/{item_id}/numeric")
async def read_items_numeric(
                item_id: Annotated[int, Path(title= "The id of an item to get", ge=1, lt=1000)],
                q: str
                ):
    '''
    Numeric validation is used to validate the value of item_id from the URL. The value of item_id must be greater than or equal to 1 and less than 1000.
    1 <= item_id < 1000
    '''
    results = {'item_id': item_id}

    if q:
        results.update({"q": q})

    return results  


#! Query Parameter Models

class FilterParams(BaseModel):
    model_config = {'extra': 'forbid'} # f a client tries to send some extra data in the query parameters, they will receive an error response.

    limit: int = Field(default=100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@router.get("/query-params")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    '''
    Query parameters validation is used to validate the value of filter_query from the URL. The value of filter_query must be a valid FilterParams object.
    '''
    return filter_query


#! Body - Multiple Parameters


## Multiple body parameters
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


@router.put("/items-mp/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    '''
    Multiple body parameters are used to validate the value of item and user from the request body. The value of item must be a valid Item object and the value of user must be a valid User object.
    '''
    results = {"item_id": item_id, "item": item, "user": user}
    return results


## Singular values in body

@router.put("/items-sv/{item_id}")
async def update_item(
    item_id: int, item: Item, 
    user: User, 
    importance: Annotated[int, Body()], # you can instruct FastAPI to treat it as another body key using Body
    q: str | None = None,  # Multiple body params and query:  Of course, you can also declare additional query parameters whenever you need, additional to any body parameters. As, by default, singular values are interpreted as query parameters, you don't have to explicitly add a Query, you can just do:
):
    '''
    singular values in body are used to validate the value of item, user, and importance from the request body. The value of item must be a valid Item object, the value of user must be a valid User object, and the value of importance must be a valid integer.
    '''
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


## Embed a single body parameter

@router.put("/items-embed/{item_id}")
async def update_item(
                item_id: int,  
                item: Annotated[Item, Body(embed=True)]
                    ):
    '''
    Let's say you only have a single item body parameter from a Pydantic model Item.

    By default, FastAPI will then expect its body directly.

    But if you want it to expect a JSON with a key item and inside of it the model contents, as it does when you declare extra body parameters, you can use the special Body parameter embed:
    

    FastAPI will expect a body like::
    {
        "item": {
            "name": "Foo",
            "description": "The pretender",
            "price": 42.0,
            "tax": 3.2
        }
    }

    instead of:
    {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    }

    '''

    results = {"item_id": item_id, "item": item}
    return results




#! Body - Fields

## Same as done in class FilterParams(BaseModel): above.



#! Body - Nested Models


## Deeply nestred models

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@router.post("/offers/")
async def create_offer(offer: Offer):
    '''
    Deeply nested models are used to validate the value of offer from the request body. The value of offer must be a valid Offer object, which contains a list of Item objects, which in turn contains a list of Image objects.
    '''
    return offer


#! Declare Request Example Data


## Extra JSON Schema data in Pydantic models
class Item1(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


@router.put("/items-examples/{item_id}")
async def update_item(item_id: int, item: Item1):
    results = {"item_id": item_id, "item": item}
    return results



## Field additional arguments

class Item2(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])


@router.put("/items-field-examples/{item_id}")
async def update_item(item_id: int, item: Item2):
    results = {"item_id": item_id, "item": item}
    return results



## Body with examples

@router.put("/items-body-examples/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results



#! Extra Data Types

from datetime import datetime, time, timedelta
from uuid import UUID


@router.put("/items-extra-data-types/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }