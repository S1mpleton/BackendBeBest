from fastapi import APIRouter, Query, Path
from pydantic import BaseModel, Field, EmailStr

from datetime import date
from typing import Union, Annotated
from dataBase import UsersModel

router = APIRouter(
    prefix="/users",
    tags=["Users👩🏻"]
)

class UserSchema(BaseModel):
    name: str
    age: int = Field(ge=14, le=150)
    mail: EmailStr



@router.get(
    "/getAll",
    summary="Get all users"
)
async def read_users():
    all_users = UsersModel.select()
    return [x.__data__ for x in all_users]



@router.get(
    "/getById/{id_user}",
    summary="Get user for ID"
)
async def read_user(id_user: Annotated[int, Path(ge=1)]):
    user = UsersModel.get_by_id(id_user)
    return user.__data__



@router.post(
    "/create",
    summary="Make user in data base"
)
async def create_user(new_user: UserSchema):
    UsersModel(
        Name = new_user.name,
        Age = new_user.age,
        Sex = 0,
        Mail = new_user.mail,
        Role = "user",
        Created_at = date.today()
    ).save()
    return {"status": "ok"}


