from fastapi import APIRouter

router = APIRouter(prefix='/day8-part-2', tags=['Day8 Part 2'])

#! Testing

## Using TestClient

# To use TestClient, first install httpx.
# Add it to your project:

#? uv add httpx

# Import TestClient.

# Create a TestClient by passing your FastAPI application to it.

# Create functions with a name that starts with test_ (this is a standard pytest convention).

# Use the TestClient object the same way as you do with httpx.

# Write simple assert statements with the standard Python expressions that you need to check (again, standard pytest).



@router.get('/')
async def read_it():
    return {'msg': "Hello World!"}


from typing import Annotated

from fastapi import Header, HTTPException
from pydantic import BaseModel

fake_secret_token = "coneofsilence"

fake_db = {
    "foo": {"id": "foo", "title": "Foo", "description": "There goes my hero"},
    "bar": {"id": "bar", "title": "Bar", "description": "The bartenders"},
}


class Item(BaseModel):
    id: str
    title: str
    description: str | None = None


@router.get("/items/{item_id}", response_model=Item)
async def read_main(item_id: str, x_token: Annotated[str, Header()]):
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]


@router.post("/items/")
async def create_item(item: Item, x_token: Annotated[str, Header()]) -> Item:
    if x_token != fake_secret_token:
        raise HTTPException(status_code=400, detail="Invalid X-Token header")
    if item.id in fake_db:
        raise HTTPException(status_code=409, detail="Item already exists")
    fake_db[item.id] = item.model_dump()
    return item


#? Install pytest.

#? uv add pytest


#? Run the tests with:

#? uv run pytest


#! Debugging

# You can connect the debugger in your editor, for example with Visual Studio Code or PyCharm.

# Call uvicorn
# In your FastAPI application, import and run uvicorn directly:

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)


import uvicorn


@router.get("/debug")
def root():
    a = "a"
    b = "b" + a
    return {"hello world": b}


if __name__ == "__main__":
    # Run the main application so this module can be executed directly for
    # quick debugging. Uvicorn expects an ASGI app, so point it at
    # the project's `main:app` (see main.py).
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)