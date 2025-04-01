from typing import Annotated

from fastapi import APIRouter, Depends

from auth.dependencies import PREFIX_AUTH, validate_auth_user, TokenUser, UserGetterByTokenType, http_bearer
from auth.utils import get_access_token, get_refresh_token, REFRESH_TOKEN_TYPE
from routers.users.schemes import GetUserSchema

router = APIRouter(
    prefix=PREFIX_AUTH,
    tags=["Auth🔒"]
)


@router.post(
    "/refresh",
    dependencies=[Depends(http_bearer)],
    response_model_exclude_none=True
)
async def update_access_user(
        user: Annotated[GetUserSchema, Depends(UserGetterByTokenType(REFRESH_TOKEN_TYPE))]
) -> TokenUser:

    access_token = get_access_token(user)
    return TokenUser(
        access_token=access_token
    )



@router.post(
    "/login",
)
async def login_user(
    user: Annotated[GetUserSchema, Depends(validate_auth_user)]
) -> TokenUser:

    access_token = get_access_token(user)
    refresh_token = get_refresh_token(user)
    return TokenUser(
        access_token=access_token,
        refresh_token=refresh_token

    )

