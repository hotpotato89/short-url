import base64
from io import BytesIO
from typing import Final

import pytest
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from src.app.core.settings import settings
from src.app.utils.qrcode import generate_qr_base64

EXAMPLE_URL: Final[str] = "https://example.com"


async def test_qr_code_is_str() -> None:
    result = generate_qr_base64(EXAMPLE_URL)

    assert isinstance(result, str)
    assert len(result) > 0
    assert result.startswith("iVBORw0KGgo")  # PNG signature in base64


async def test_qr_code_direction() -> None:
    result = generate_qr_base64(EXAMPLE_URL)
    byte = base64.b64decode(result)
    image = Image.open(BytesIO(byte))

    decoded_data = decode(image)
    assert len(decoded_data) == 1

    actual_url = decoded_data[0].data.decode()
    expected_url = EXAMPLE_URL

    assert actual_url == expected_url
