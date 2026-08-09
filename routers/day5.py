from fastapi import APIRouter, File, UploadFile, Form
from typing import Annotated
from fastapi.responses import HTMLResponse

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


