from fastapi import APIRouter, Depends, Cookie, Header, HTTPException
from pydantic import BaseModel
from typing import Annotated


router = APIRouter(prefix='/day6', tags=['Day 6'])


#! Classes as Dependencies

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

common_param = Annotated[CommonQueryParams, Depends(CommonQueryParams)]
@router.get("/items/")
async def read_items(
    # commons: Annotated[CommonQueryParams, Depends()]  # You declare the dependency as the type of the parameter, and you use Depends() without any parameter, instead of having to write the full class again inside of Depends(CommonQueryParams).

    # commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]

    commons: common_param

    ):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response



#! Sub-dependencies

def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = None,
):
    if not q:
        return last_query
    return q


@router.get("/items-sub-dependencies/")
async def read_query(
    query_or_default: Annotated[str, Depends(query_or_cookie_extractor)],
):
    return {"q_or_cookie": query_or_default}



## Using the same dependency multiple times

# If one of your dependencies is declared multiple times for the same path operation, for example, multiple dependencies have a common sub-dependency, FastAPI will know to call that sub-dependency only once per request.

# And it will save the returned value in a "cache" and pass it to all the "dependants" that need it in that specific request, instead of calling the dependency multiple times for the same request.

# In an advanced scenario where you know you need the dependency to be called at every step (possibly multiple times) in the same request instead of using the "cached" value, you can set the parameter use_cache=False when using Depends:



async def needy_dependency(fresh_value: Annotated[str, Depends(query_or_cookie_extractor, use_cache=False)]):
    return {"fresh_value": fresh_value}




#! Dependencies in path operation decorators

# These dependencies will be executed/solved the same way as normal dependencies. But their value (if they return any) won't be passed to your path operation function.

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@router.get("/items-dep-path/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]



#!Global Dependencies


# Similar to the way you can add dependencies to the path operation decorators, you can add them to the FastAPI application.

# In that case, they will be applied to all the path operations in the application:

#? app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])



#! Dependencies with yield

# If you catch an exception in a dependency with yield, unless you are raising another HTTPException or similar, you should re-raise the original exception.
# yield: "Here's the database. Pause this dependency while the endpoint runs. When the endpoint is finished, come back here and do the cleanup."

# You can re-raise the same exception using raise:

data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}


class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


@router.get("/items-yield/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError(username)
    return item


## Always raise in Dependencies with yield and except

# If you catch an exception in a dependency with yield, unless you are raising another HTTPException or similar, you should re-raise the original exception.

# You can re-raise the same exception using raise

class InternalError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except InternalError:
        print("We don't swallow the internal error here, we raise again 😎")
        raise     


@router.get("/items-raise/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id == "portal-gun":
        raise InternalError(
            f"The portal gun is too dangerous to be owned by {username}"
        )
    if item_id != "plumbus":
        raise HTTPException(
            status_code=404, detail="Item not found, there's only a plumbus here"
        )
    return item_id