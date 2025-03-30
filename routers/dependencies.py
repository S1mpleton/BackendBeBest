from typing import Annotated, Union

from fastapi import HTTPException, status
from peewee import ModelSelect
from pydantic import BaseModel, Field

from config import IMAGE_DIR
from dataBase import ImageUserModel, ImageCourseModel, ImageModuleModel

allowed_mime_types = ["image/jpeg", "image/png"]

USER_TYPE = "user"
COURSE_TYPE = "course"
MODULE_TYPE = "module"



class FeaturedImageSchema(BaseModel):
    original: Annotated[Union[str, None], Field()] = None
    small:  Annotated[Union[str, None], Field()] = None


class GetPaginationSchema(BaseModel):
    number_page: Annotated[Union[int, None], Field(ge=1)] = None
    quantity_on_page: Annotated[Union[int, None], Field(ge=1)] = None

class PaginationSchema(BaseModel):
    current_page: int
    total_pages: int
    total_elements: int



def get_image_path(
        id_model: int,
        name_model: str,
        format_name: str
):
    file_name = f"{id_model}-{name_model}-{format_name}.jpg"
    file_path = IMAGE_DIR.joinpath(file_name)
    return file_path


def get_featured_image(db_request: ModelSelect) -> FeaturedImageSchema:
    images = {}
    for f in db_request:
        images[f.format.format_name] = f.image_path

    return FeaturedImageSchema(**images)


def check_image_format(content_type):
    if content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. File isn't PNG, JPEG"
        )
