from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel

from auth.hashing import verify_password
from auth.utils_jwt import encode_jwt, decode_jwt
from dataBase.repository import UserRepository
from routers.schemes import LoginUserSchema, GetUserSchema



router = APIRouter(
    prefix="/auth",
    tags=["Auth🔒"]
)

oauth2_shem = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

class TokenUser(BaseModel):
    access_token: str
    token_type: str


def check_token(
    token: Annotated[str, Depends(oauth2_shem)]
) -> dict:
    try:
        return decode_jwt(jwt_token=token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

def get_user_id_by_jwt(
    payload: Annotated[dict, Depends(check_token)]
):
    return payload.get("sub")

def get_user_by_jwt(
    payload: Annotated[dict, Depends(check_token)]
) -> GetUserSchema:
    user = UserRepository.get_by_id(payload.get("sub"))
    return user



def validate_auth_user(
    username: str = Form(),
    password: str = Form()
) -> LoginUserSchema:
    un_auth_ecx = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid login or password"
    )
    user = UserRepository.get_user_for_email(username)
    if not user:
        raise un_auth_ecx

    if verify_password(plain_password=password, hashed_password=user.hashed_password):
        return LoginUserSchema(**user.__data__)
    raise un_auth_ecx



@router.post(
    "/login",
)
async def login_user(
    user: Annotated[LoginUserSchema, Depends(validate_auth_user)]
) -> TokenUser:
    jwt_payload = {
        "sub": user.id,
        "username": user.name,
        "email": user.mail
    }
    token = encode_jwt(jwt_payload)
    return TokenUser(
        access_token = token,
        token_type = "Bearer"
    )

