from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from config import CERTS_DIR, IMAGE_DIR


def generate_keys():
    if not IMAGE_DIR.parent.is_dir():
        IMAGE_DIR.parent.mkdir()

    if not IMAGE_DIR.is_dir():
        IMAGE_DIR.mkdir()

    if not CERTS_DIR.is_dir():
        CERTS_DIR.mkdir()

    # Генерация секретного ключа
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Получение публичного ключа из секретного
    public_key = private_key.public_key()

    # Сериализация секретного ключа в PEM формате
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Сериализация публичного ключа в PEM формате
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(CERTS_DIR.joinpath("private.pem"), "wb") as file:
        file.write(pem_private)

    with open(CERTS_DIR.joinpath("public.pem"), "wb") as file:
        file.write(pem_public)

