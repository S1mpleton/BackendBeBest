from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr

from datetime import date
from typing import Union, Annotated
from dataBase import UsersModel

from enum import Enum

router = APIRouter(
    prefix="/users",
    tags=["Users👩🏻"]
)

class UserRole(str, Enum):
    user = "user"
    editor = "editor"
    administrator = "administrator"


class UserSchema(BaseModel):
    Name: str = Field(max_length=25, default="Гость")
    Age: int = Field(ge=14, le=150, default=0)
    Sex: int = Field(ge=0, le=2, default=0)
    Mail: EmailStr
    Role: UserRole = Field(default=UserRole.user)

class UserWithDateSchema(UserSchema):
    Created_at: date



@router.get(
    "/getAll",
    summary="Get all users"
)
async def read_users() -> list[UserWithDateSchema]:

    all_users = UsersModel.select()
    return [x.__data__ for x in all_users]



@router.get(
    "/getById/{id_user}",
    summary="Get user for ID"
)
async def read_user(id_user: Annotated[int, Path(ge=1)]) -> UserWithDateSchema:
    try:
        user = UsersModel.get_by_id(id_user)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return user.__data__
    finally:
        pass



@router.patch(
    "/update/{id_user}",
    summary="Update user for ID"
)
async def create_user(
        id_user: Annotated[int, Path(ge=1)],
        new_data_user: Annotated[UserSchema, Body()]
):
    user = UsersModel.get_by_id(id_user)

    user.name = new_data_user.name
    user.age = new_data_user.age
    user.sex = new_data_user.sex
    user.mail = new_data_user.mail
    return {"status": "ok"}


@router.post(
    "/create",
    summary="Make user in data base"
)
async def create_user(new_user: Annotated[UserSchema, Depends()]):
    UsersModel(
        Name = new_user.Name,
        Age = new_user.Age,
        Sex = 0,
        Mail = new_user.Mail,
        Role = new_user.Role,
        Created_at = date.today()
    ).save()
    return {"status": "ok"}


