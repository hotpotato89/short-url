from passlib.context import CryptContext

from src.app.core.settings import settings

pwd_context = CryptContext(
    ["argon2"],
    deprecated="auto",
    argon2__time_cost=settings.argon2.time_cost,
    argon2__memory_cost=settings.argon2.memory_cost,
    argon2__parallelism=settings.argon2.parallelism,
    argon2__hash_len=settings.argon2.hash_len,
    argon2__salt_len=settings.argon2.salt_len,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)
