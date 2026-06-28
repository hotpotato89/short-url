from hashlib import sha256

class CryptUtil:
    def hash(self, token: str) -> str:
        return sha256(token.encode()).hexdigest()


crypt_util = CryptUtil()
