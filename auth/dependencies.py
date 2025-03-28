from typing import Annotated, Union

from fastapi import Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jwt import InvalidTokenError
from pydantic import BaseModel

from auth.hashing import verify_password
from auth.utils import decode_jwt, TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from routers.users.repository import UserRepository
from routers.users.schemes import GetUserSchema

PREFIX_AUTH = "/auth"


class TokenUser(BaseModel):
    access_token: str
    refresh_token: Union[str, None] = None
    token_type: str = "Bearer"


oauth2_shem = OAuth2PasswordBearer(
    tokenUrl=f"{PREFIX_AUTH}/login"
)

http_bearer = HTTPBearer(auto_error=True)


def check_current_token(
        token: Annotated[str, Depends(oauth2_shem)]
) -> dict:
    try:
        return decode_jwt(jwt_token=token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")


def validate_auth_user(
        username: str = Form(),
        password: str = Form()
) -> GetUserSchema:
    user = UserRepository.get_user_for_email(username)

    hashed_password = UserRepository.get_hashed_password(user)
    if verify_password(plain_password=password, hashed_password=hashed_password):
        return user

    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password or email"
        )



class UserGetterByTokenType:
    @classmethod
    def validate_token_type(
            cls,
            payload: dict,
            token_type: str
    ) -> bool:
        current_type = payload.get(TOKEN_TYPE_FIELD)
        if current_type == token_type:
            return True

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type expected {token_type!r}"
        )

    def __init__(self, token_type: str):
        self.token_type = token_type

    def __call__(
            self,
            payload: Annotated[dict, Depends(check_current_token)]
    ) -> GetUserSchema:
        self.validate_token_type(payload, self.token_type)
        return UserRepository.get_by_id(payload.get("sub"))


