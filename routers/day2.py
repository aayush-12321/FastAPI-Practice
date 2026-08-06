from fastapi import APIRouter, FastAPI, Query
from typing import Annotated
from pydantic import BaseModel, AfterValidator
import random

# app = FastAPI()

router = APIRouter(prefix="/day-2", tags=["Day 2"])

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


#! Query Parameter

@router.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    '''
    Query parameters are used to filter or modify the response of an endpoint.
    In this example, we use skip and limit query parameters to paginate the results.
    '''
    return fake_items_db[skip : skip + limit]


@router.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    '''
    We can declare optional query parameters, by setting their default to None:
    '''

    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


@router.get("/users/{user_id}/item/{item_id}")
async def read_user_item(user_id: int, item_id:str, q:str | None=None, short:bool = False):
    '''
    Can declare multiple path parameters and query parameters at the same time, FastAPI knows which is which.
    And we don't have to declare them in any specific order.   
    '''

    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})

    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item



#! Request Body
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@router.post("/items/")
async def create_item(item: Item):
    '''
    We can declare a request body using Pydantic models. 
    In this example, we use the Item model to validate the request body.
    '''

    item_dict = item.model_dump()

    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price with tax": price_with_tax})
    return item_dict


#! Query paramaters and string validators

@router.get("/items/validate/")
async def read_items(q: Annotated[
                            str | None, 
                            Query(
                                min_length=3, 
                                max_length=7, 
                                pattern="^[a-zA-Z0-9]+$",
                                title="Query String",
                                description="Query string for the items to search in the database that have a good match",
                                deprecated=True,  # you don't like this parameter anymore. You have to leave it there a while because there are clients using it, but you want the docs to clearly show it as deprecated.

                                )] = None,
                    hidden_query: Annotated[
                            str | None, 
                            Query(
                                include_in_schema=False,  #To exclude a query parameter from the generated OpenAPI schema 

                                )] = None

                            ):
    '''
    Query parameters can have additional validation rules, such as minimum and maximum length, regex patterns, and more. 
    In this example, we use the Query class to add validation rules to the q query parameter.
    '''

    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}

    if q:
        results.update({"q": q})

    if hidden_query:
        results.update({"hidden_query": hidden_query})
    return results


## Custom Validation

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

@router.get("/items/custom-validator/")
async def read_item_custom_validator(id: Annotated[str | None, AfterValidator(check_valid_id)]  = None):
    '''
    We can create custom validation functions and use them with the AfterValidator class to validate query parameters.
    '''
    if id:
        title = data.get(id)

    else:
        id, title = random.choice(list(data.items()))

    return {"id": id, "title": title}


## Query parameter list / multiple values¶
@router.get("/query-list/")
async def read_items(q: Annotated[list[str], Query()] = ["foo", "bar"]):
    '''
    To declare a query parameter with a type of list, like in the example above, you need to explicitly use Query, otherwise it would be interpreted as a request body.
    '''
    query_items = {"q": q}
    return query_items


## Alias parameters
@router.get("/alias-params/")
async def read_items(q: Annotated[str | None, Query(alias="item-query")] = None):
    '''
    Imagine that you want the parameter to be item-query.
    But you want to use a valid Python variable name in your function, so you use q as the parameter name.
    
    As you cannot use 'item-query' as a parameter name, you can use the alias parameter to declare the query parameter name in the URL.
    '''
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results