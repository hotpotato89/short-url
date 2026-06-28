import pytest
from src.app.utils.crypt import crypt_util


def test_hash_token():
    token = "my_refresh_token"
    hashed = crypt_util.hash(token)
    
    assert isinstance(hashed, str)
    assert len(hashed) == 64  # SHA-256
    assert hashed != token


def test_hash_consistent():
    token = "my_refresh_token"
    
    hash1 = crypt_util.hash(token)
    hash2 = crypt_util.hash(token)
    
    assert hash1 == hash2


def test_hash_different_tokens():
    token1 = "token1"
    token2 = "token2"
    
    hash1 = crypt_util.hash(token1)
    hash2 = crypt_util.hash(token2)
    
    assert hash1 != hash2