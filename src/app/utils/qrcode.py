from io import BytesIO
import base64

import qrcode
from PIL import Image


def generate_qr_base64(data: str, box_size: int = 10, border: int = 4) -> str:
    """Generate Qrcode and return as base64 string"""

    qr = qrcode.QRCode(version=1, box_size=box_size, border=border)
    qr.add_data(data=data)
    qr.make(fit=True)

    image: Image.Image = qr.make_image(fill_color="black", back_color="white") #type: ignore

    if not isinstance(image, Image.Image):
        image = image.convert('RGB')

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_bytes = buffered.getvalue()

    return base64.b64encode(image_bytes).decode()
