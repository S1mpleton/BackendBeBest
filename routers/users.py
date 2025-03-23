from fastapi import APIRouter, Path, Depends

from typing import Annotated

from auth.auth import get_user_by_jwt, get_user_id_by_jwt

from dataBase.repository import UserRepository
from routers.schemes import GetUserSchema, CreateUserSchema, UpdateUserSchema






router = APIRouter(
    prefix="/users",
    tags=["Users👩🏻"]
)



@router.get(
    "/me",
    summary="Get authorized user"
)
async def get_authorized_user(
        user: Annotated[GetUserSchema, Depends(get_user_by_jwt)]
) -> GetUserSchema:
    return user


@router.get(
    "/getById/{id_user}",
    summary="Get user for ID"
)
async def read_user(id_user: Annotated[int, Path(ge=1)]) -> GetUserSchema:
    return UserRepository.get_by_id(id_user)


@router.post(
    "/create",
    summary="Make user in data base"
)
async def create_user(new_user: Annotated[CreateUserSchema, Depends()]) -> GetUserSchema:
    return UserRepository.create(new_user)



@router.patch(
    "/updateById",
    summary="Update user"
)
async def update_user(
        id_user: Annotated[int, Depends(get_user_id_by_jwt)],
        data: Annotated[UpdateUserSchema, Depends()]
) -> GetUserSchema:
    return UserRepository.update_user(id_user, data)



@router.delete(
    "/deleteById/{id_user}",
    summary="Delete user by id, courses that was created this user, also deleted"
)
async def delete_user(id_user: Annotated[int, Path(ge=1)]):
    UserRepository.delete_by_id(id_user)
    return {"status": "ok"}













