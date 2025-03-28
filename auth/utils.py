from datetime import timedelta, datetime
from typing import Union

import jwt

from config import AuthJWT, SETTINGS
from routers.users.schemes import GetUserSchema



TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def encode_jwt(
        payload: dict,
        private_key: str = AuthJWT().private_key_path.read_text(),
        algorithm: str = AuthJWT().algorithm,
        expire_minutes: int = AuthJWT().access_token_expire_minutes,
        expire_timedelta: Union[timedelta, None] = None
) -> str:
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
    print("DECODE JWT", decoded)
    return decoded







def create_jwt(
        token_type: str,
        payload: dict,
        expire_minutes: int = SETTINGS.auth_JWT.access_token_expire_minutes,
        expire_timedelta: Union[timedelta, None] = None
) -> str:
    jwt_payload =  {
        TOKEN_TYPE_FIELD: token_type
    }

    jwt_payload.update(payload)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )


def get_access_token(
        user: GetUserSchema
) -> str:
    jwt_payload = {
        "sub": user.id,
        "username": user.name,
        "email": user.email
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=SETTINGS.auth_JWT.access_token_expire_minutes
    )


def get_refresh_token(
        user: GetUserSchema
) -> str:
    jwt_payload = {
        "sub": user.id,
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_timedelta=timedelta(days=SETTINGS.auth_JWT.refresh_token_expire_days)
    )


