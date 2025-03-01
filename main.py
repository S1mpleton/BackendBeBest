
from typing import Union
from enum import Enum
from datetime import date

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from dataBase.data import db, UsersModel

#GVT
#токен
#UI
#Яндекс трекер

class UserSchema(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    mail: EmailStr
    role: Union[str, None]
    password: str




app = FastAPI()


@app.get(
    "/users/get/all",
    tags=["Users👩🏻"],
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


@app.get(
    "/users/get/id/{id_user}",
    tags=["Users👩🏻"],
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


@app.post("/users/create")
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


# class ModelName(str, Enum):
#     alexnet = "alexn1et"
#     resnet = "resnet"
#     lenet = "lenet"

# @app.get("/models/{model_name}")
# async def get_model(model_name: ModelName):
#     if model_name is ModelName.alexnet:
#         return {"model_name": model_name, "message": "Deep Learning FTW!"}
#
#     if model_name.value == "lenet":
#         return {"model_name": model_name, "message": "LeCNN all the images"}
#
#     return {"model_name": model_name, "message": "Have some residuals"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)