from fastapi import APIRouter, Depends, Cookie
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