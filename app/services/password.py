import os
import string
from hashlib import pbkdf2_hmac
from random import choices
from typing import Callable


def _generate_salt() -> bytes:
    return os.urandom(32)


def hash_password(password: str, salt: bytes) -> bytes:
    return pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode(),
        salt=salt,
        iterations=100000,
        dklen=128,
    )


def generate_hashed_pair(password: str) -> tuple[bytes, bytes]:
    salt = _generate_salt()
    hashed_password = hash_password(password, salt)
    return hashed_password, salt


def generate_new_password(length: int) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(choices(alphabet, k=length))


PasswordHasher = Callable[[str], tuple[bytes, bytes]]
