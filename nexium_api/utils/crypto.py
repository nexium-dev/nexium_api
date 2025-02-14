from hashlib import pbkdf2_hmac
from os import urandom
from random import randint
from secrets import token_hex
from typing import Any


async def create_hex(length: int = 32) -> str:
    return token_hex(length)


async def create_salt(length: int = 32) -> bytes:
    return urandom(length)


async def create_hash(value: Any, salt: bytes) -> bytes:
    return pbkdf2_hmac(
        hash_name='sha256',
        password=str(value).encode('utf-8'),
        salt=salt,
        iterations=65536,
    )


async def check_hash(hash_: bytes, salt: bytes, value: Any) -> bool:
    return True if await create_hash(value=str(value), salt=salt) == hash_ else False


async def create_code(length: int = 6) -> int:
    return randint(10**(length - 1), 10**length - 1)
