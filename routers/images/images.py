import os.path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from .repository import ImagesRepository

router = APIRouter(
    prefix="/images",
    tags=["Images🎨"]
)

@router.get(
    "/getByName/{image_name}/",
    summary="Get image for name"
)
async def read_image_for_name(image_name: str)-> FileResponse:
    return ImagesRepository.get_response_image(image_name)


