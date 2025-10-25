import qrcode
from io import BytesIO

def create_QR_code(url):
    qr_image = qrcode.make(url)
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_filename = f"qr_{url}.png"
    return qr_filename, buffer