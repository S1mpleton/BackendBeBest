import datetime
from typing import Annotated, Union

from fastapi import UploadFile, File, Path, Query
from pydantic import BaseModel, Field, HttpUrl

from routers.dependencies import FeaturedImageSchema, PaginationSchema, GetPaginationSchema


class ModuleSchema(BaseModel):
    course_id: int = Field(ge=1)
    title: str = Field(max_length=150, default="title")
    description: str = Field(max_length=600, default="description")
    video_URL: HttpUrl

class GetModuleSchema(ModuleSchema):
    id: int = Field(ge=1)
    created_at: datetime.date
    featuredImage: FeaturedImageSchema

class CreateModuleSchema(ModuleSchema):
    image: Annotated[UploadFile, File()]

class PaginationModuleSchema(BaseModel):
    data: list[GetModuleSchema]
    pagination: PaginationSchema

class UpdateModuleSchema(BaseModel):
    id: Annotated[int, Path(ge=1)]
    title: Annotated[Union[str, None], Query(max_length=50)] = None
    description: Annotated[Union[str, None], Query(max_length=600)] = None
    video_url: Annotated[Union[HttpUrl, None], Query()] = None
    image: Annotated[Union[UploadFile, None], File()] = None

class GetPaginationModuleSchema(GetPaginationSchema):
    description: Annotated[Union[str, None], Path(max_length=50)] = None
