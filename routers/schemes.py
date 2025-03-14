from datetime import date
from enum import Enum
from typing import Union, Annotated

from fastapi import UploadFile, File
from pydantic import BaseModel, Field, HttpUrl, EmailStr




allowed_mime_types = ["image/jpeg", "image/png"]

class FeaturedImageSchema(BaseModel):
    original: Annotated[Union[str, None], Field()] = None
    small:  Annotated[Union[str, None], Field()] = None

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


# --- Users schemes ---

class UserRole(str, Enum):
    user = "user"
    editor = "editor"
    administrator = "administrator"


class UserSchema(BaseModel):
    name: str = Field(max_length=25, default="Гость")
    mail: EmailStr


class CreateUserSchema(UserSchema):
    password: str = Field(max_length=60)


class GetUserSchema(UserSchema):
    id: int = Field(ge=1)
    age: Annotated[Union[int, None], Field(ge=14, le=150)] = None
    sex: Annotated[Union[int, None], Field(ge=0, le=2)] = None
    password: str = Field(max_length=60)
    role: UserRole = Field(default=UserRole.user)
    created_at: date
    featuredImage: FeaturedImageSchema

class UpdateUserSchema(BaseModel):
    name: Annotated[Union[str, None], Field(max_length=25)] = None
    mail: Annotated[Union[EmailStr, None], Field()] = None
    password: Annotated[Union[str, None], Field(max_length=60)] = None
    age: Annotated[Union[int, None], Field(ge=14, le=150)] = None
    sex: Annotated[Union[int, None], Field(ge=0, le=2)] = None
    image: Annotated[Union[UploadFile, None], File()] = None