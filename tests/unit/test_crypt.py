from cryptography.fernet import InvalidToken
import pytest
from src.app.utils.crypt import crypt_util


def test_encrypt_decrypt():
    original = "my_secret_token"
    
    encrypted = crypt_util.encrypt(original)
    assert encrypted is not None
    assert encrypted != original
    
    decrypted = crypt_util.decrypt(encrypted)
    assert decrypted == original


def test_decrypt_invalid_token():
    with pytest.raises(InvalidToken):
        crypt_util.decrypt('invalid_token')


def test_encrypt_different_tokens():
    token1 = "token1"
    token2 = "token2"
    
    encrypted1 = crypt_util.encrypt(token1)
    encrypted2 = crypt_util.encrypt(token2)
    
    assert encrypted1 != encrypted2
    assert crypt_util.decrypt(encrypted1) == token1
    assert crypt_util.decrypt(encrypted2) == token2