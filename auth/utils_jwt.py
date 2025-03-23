from datetime import timedelta, datetime
from typing import Union

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from config import AuthJWT, PWD_CONTEXT
from dataBase import UsersModel


class TokenUser(BaseModel):
    access_token: str
    token_type: str



def encode_jwt(
    payload: dict,
    private_key: str = AuthJWT().private_key_path.read_text(),
    algorithm: str = AuthJWT().algorithm,
    expire_minutes: int = AuthJWT().access_token_expire_minutes,
    expire_timedelta: Union[timedelta, None] = None
):
    to_encode = payload.copy()
    now_date_time = datetime.utcnow()
    if expire_timedelta:
        expire = now_date_time + expire_timedelta
    else:
        expire = now_date_time + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now_date_time
    )
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    jwt_token: Union[str, bytes],
    public_key: str = AuthJWT().public_key_path.read_text(),
    algorithm: str = AuthJWT().algorithm
):
    decoded = jwt.decode(jwt_token, public_key, algorithms=[algorithm])
    return decoded





def authenticate_user(fake_db: UsersModel, mail: str, password: str):
    user = fake_db.select().where(fake_db.mail == mail).first()
    pass
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user