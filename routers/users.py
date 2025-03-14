from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr

from datetime import date
from typing import Union, Annotated
from dataBase import UsersModel

from enum import Enum

from dataBase.repository import UserRepository
from routers.schemes import GetUserSchema, CreateUserSchema, UpdateUserSchema

router = APIRouter(
    prefix="/users",
    tags=["Users👩🏻"]
)



@router.get(
    "/getById/{id_user}",
    summary="Get user for ID"
)
async def read_user(id_user: Annotated[int, Path(ge=1)]) -> GetUserSchema:
    try:
        return UserRepository.get_by_id(id_user)

    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

    finally:
        pass



@router.post(
    "/create",
    summary="Make user in data base"
)
async def create_user(new_user: Annotated[CreateUserSchema, Depends()]) -> GetUserSchema:
    return UserRepository.create(new_user)



@router.put(
    "/updateById/{id_user}",
    summary="Update user for ID"
)
async def update_user(
        id_user: Annotated[int, Path(ge=1)],
        data: Annotated[UpdateUserSchema, Depends()]
) -> GetUserSchema:
    return UserRepository.update_user(id_user, data)




@router.delete(
    "/deleteById/{id_user}",
    summary="Delete user by id, courses that was created this user, also deleted"
)
async def delete_course(id_user: Annotated[int, Path(ge=1)]):
    UserRepository.delete_by_id(id_user)
    return {"status": "ok"}




