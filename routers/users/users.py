from fastapi import APIRouter, Path, Depends, HTTPException, status

from typing import Annotated

from auth.dependencies import UserGetterByTokenType
from auth.utils import ACCESS_TOKEN_TYPE
from routers.users.repository import UserRepository
from routers.users.schemes import GetUserSchema, CreateUserSchema, UpdateUserSchema, UserRole

router = APIRouter(
    prefix="/users",
    tags=["Users👩🏻"]
)




@router.get(
    "/me",
    summary="Get authorized user"
)
async def get_authorized_user(
        user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
) -> GetUserSchema:
    return user


@router.get(
    "/getById/{id_user}",
    summary="Get user for ID"
)
async def read_user(
        id_user: Annotated[int, Path(ge=1)],
         user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
) -> GetUserSchema:
    return UserRepository.get_by_id(id_user)

@router.get(
    "/getAll",
    summary="Get all users"
)
async def read_user() -> list[GetUserSchema]:
    return UserRepository.get_all()


@router.post(
    "/create",
    summary="Make user in data base"
)
async def create_user(new_user: Annotated[CreateUserSchema, Depends()]) -> GetUserSchema:
    return UserRepository.create(new_user)



@router.patch(
    "/update",
    summary="Update authorized user"
)
async def update_user(
        user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))],
        data: Annotated[UpdateUserSchema, Depends()]
) -> GetUserSchema:
    return UserRepository.update_user(user.id, data)



@router.delete(
    "/delete",
    summary="Delete authorized user, courses that was created this user, also deleted"
)
async def delete_user(
        user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
):
    UserRepository.delete_by_id(user.id)
    return {"status": "ok"}



@router.delete(
    "/deleteById/{id_user}",
    summary="Delete user by id, courses that was created this user, also deleted"
)
async def delete_user_by_id(
        id_user: Annotated[int, Path(ge=1)],
        administrator: Annotated[GetUserSchema, Depends(UserGetterByTokenType(ACCESS_TOKEN_TYPE))]
):
    if administrator.role == UserRole.administrator:
        UserRepository.delete_by_id(id_user)
        return {"status": "ok"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="no access"
    )













