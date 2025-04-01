import datetime
from enum import Enum
from typing import Annotated, Union

from fastapi import UploadFile, File, Path, Query
from pydantic import BaseModel, Field

from routers.dependencies import FeaturedImageSchema, PaginationSchema, GetPaginationSchema


class CategoryCourse(str, Enum):
    health = "Health"
    finance = "Finance"
    management = "Management"

class CourseSchema(BaseModel):
    creator_id: int = Field(ge=1)
    title: str = Field(max_length=50, default="title")
    description: str = Field(max_length=600, default="description")

class GetCourseSchema(CourseSchema):
    id: int = Field(ge=1)
    created_at: datetime.date
    featuredImage: FeaturedImageSchema

class CreateCourseSchema(CourseSchema):
    image: UploadFile = File()

class PaginationCourseSchema(BaseModel):
    data: list[GetCourseSchema]
    pagination: PaginationSchema

class UpdateCourseSchema(BaseModel):
    id: Annotated[int, Field(ge=1)]
    title: Annotated[Union[str, None], Field(max_length=50)] = None
    description: Annotated[Union[str, None], Field(max_length=600)] = None
    image: Annotated[Union[UploadFile, None], File()] = None


class GetPaginationCourseSchema(GetPaginationSchema):
    description: Annotated[Union[str, None], Path(max_length=50)] = None
    category: Annotated[Union[CategoryCourse, None], Field()] = None
