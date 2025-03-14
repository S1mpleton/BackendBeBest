import os.path
from typing import Annotated

from fastapi import Path, APIRouter
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/images",
    tags=["Images🎨"]
)

@router.get(
    "/getByName/{image_name}/",
    summary="Get image for name"
)
async def read_image_for_name(image_name: str)-> FileResponse:
    image_path = os.path.join("resources", "images", image_name)
    return FileResponse(image_path)


