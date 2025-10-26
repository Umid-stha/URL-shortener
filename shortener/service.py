import qrcode
from io import BytesIO
import logging

logger = logging.getLogger('__name__')

def create_QR_code(url, short_url):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        file_name = f"qr_{short_url}.png"
        logger.info(f"✅ QR code created successfully for {short_url}")
        return file_name, buffer 
    except Exception as e:
        logger.error(f"❌ QR generation failed for {short_url}: {e}", exc_info=True)
        return '', None