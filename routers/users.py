from fastapi import APIRouter
from pydantic import BaseModel, Field, EmailStr

from datetime import date
from typing import Union
from dataBase import UsersModel

router = APIRouter(
    prefix="/users",
    tags=["Users👩🏻"]
)

class UserSchema(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    mail: EmailStr
    role: Union[str, None]
    password: str



@router.get(
    "/get/all",
    summary="Get all users"
)
async def read_users():
    all_users = []
    for user in UsersModel.select():
        all_users.append({
            "ID": user.ID,
            "name": user.Name,
            "age": user.Age,
            "mail": user.Mail,
            "role": user.Role,
            "password": user.Password,
            "created_at": user.Created_at
        })
    return all_users


@router.get(
    "/get/id/{id_user}",
    summary="Get user for ID"
)
async def read_user(id_user: int):
    user = UsersModel.get(ID=id_user)
    return {
        "ID": user.ID,
        "name": user.Name,
        "age": user.Age,
        "mail": user.Mail,
        "role": user.Role,
        "password": user.Password,
        "created_at": user.Created_at
    }


@router.post(
    "/users/create",
    summary="Make user in data base"
)
async def create_user(new_user: UserSchema):
    UsersModel(
        Name = new_user.name,
        Age = new_user.age,
        Mail = new_user.mail,
        Role = new_user.role,
        Password = new_user.password,
        Created_at = date.today()
    ).save()
    return {"status": "ok"}
