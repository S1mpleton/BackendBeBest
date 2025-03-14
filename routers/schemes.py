from datetime import date

from fastapi import UploadFile, File
from pydantic import BaseModel, Field, HttpUrl




allowed_mime_types = ["image/jpeg", "image/png"]

class FeaturedImageSchema(BaseModel):
    original: str
    small: str

class PaginationSchema(BaseModel):
    current_page: int
    total_pages: int
    total_elements: int


# --- Courses schemes ---

class CourseSchema(BaseModel):
    creator_id: int = Field(ge=1)
    title: str = Field(max_length=50, default="title")
    description: str = Field(max_length=600, default="description")

class GetCourseSchema(CourseSchema):
    id: int = Field(ge=1)
    created_at: date
    featuredImage: FeaturedImageSchema

class CreateCourseSchema(CourseSchema):
    image: UploadFile = File()

class PaginationCourseSchema(BaseModel):
    data: list[GetCourseSchema]
    pagination: PaginationSchema


# --- Modules schemes ---

class ModuleSchema(BaseModel):
    course_id: int = Field(ge=1)
    title: str = Field(max_length=50, default="title")
    description: str = Field(max_length=600, default="description")
    video_URL: HttpUrl

class GetModuleSchema(ModuleSchema):
    id: int = Field(ge=1)
    created_at: date
    featuredImage: FeaturedImageSchema

class CreateModuleSchema(ModuleSchema):
    image: UploadFile = File()

class PaginationModuleSchema(BaseModel):
    data: list[GetModuleSchema]
    pagination: PaginationSchema