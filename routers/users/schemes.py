import datetime
from enum import Enum
from typing import Annotated, Union

from fastapi import UploadFile, File
from pydantic import BaseModel, Field, EmailStr

from routers.dependencies import FeaturedImageSchema


class UserRole(str, Enum):
    user = "user"
    editor = "editor"
    administrator = "administrator"


class UserSchema(BaseModel):
    name: str = Field(max_length=100, default="Гость")
    email: EmailStr


class CreateUserSchema(UserSchema):
    password: str = Field(max_length=60)


class GetUserSchema(UserSchema):
    id: int = Field(ge=1)
    age: Annotated[Union[int, None], Field(ge=14, le=150)] = None
    sex: Annotated[Union[int, None], Field(ge=0, le=2)] = None
    role: UserRole = Field(default=UserRole.user)
    created_at: datetime.date
    featuredImage: FeaturedImageSchema

class UpdateUserSchema(BaseModel):
    name: Annotated[Union[str, None], Field(max_length=25)] = None
    email: Annotated[Union[EmailStr, None], Field()] = None
    password: Annotated[Union[str, None], Field(max_length=60)] = None
    age: Annotated[Union[int, None], Field(ge=14, le=150)] = None
    sex: Annotated[Union[int, None], Field(ge=0, le=2)] = None
    image: Annotated[Union[UploadFile, None], File()] = None