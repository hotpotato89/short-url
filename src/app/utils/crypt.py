from logging import getLogger

from cryptography.fernet import Fernet, InvalidToken

from src.app.core.exceptions import InvalidTokenError
from src.app.core.settings import settings


logger = getLogger(__name__)


class CryptUtil:
    def __init__(self) -> None:
        self._fernet = Fernet(settings.fernet.secret_key.get_secret_value().encode())

    def encrypt(self, token: str) -> str:
        return self._fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        return self._fernet.decrypt(encrypted_token.encode()).decode()


crypt_util = CryptUtil()
