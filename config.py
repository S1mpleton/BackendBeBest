from pathlib import Path

from passlib.context import CryptContext
from pydantic import BaseModel




BASE_DIR = Path(__file__).parent

CERTS_DIR = BASE_DIR.joinpath("certs")

DB_DIR = BASE_DIR.joinpath("dataBase")

IMAGE_DIR = BASE_DIR.joinpath("resources").joinpath("images")

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")








class AuthJWT(BaseModel):
    private_key_path: Path = CERTS_DIR.joinpath("private.pem")
    public_key_path: Path = CERTS_DIR.joinpath("public.pem")
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class Settings(BaseModel):
    auth_JWT: AuthJWT = AuthJWT()