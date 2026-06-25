import pytest

from src.app.utils.qrcode import generate_qr_base64


async def test_qr_code_is_str() -> None:
    data = 'https://example.com'
    result = generate_qr_base64(data)

    assert isinstance(result, str)
    assert len(result) > 0
    assert result.startswith('iVBORw0KGgo') # PNG signature in base64
