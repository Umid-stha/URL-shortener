import qrcode
from io import BytesIO

def create_QR_code(url, short_url):
    qr_image = qrcode.make(url)
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_filename = f"qr_{short_url}.png"
    return qr_filename, buffer