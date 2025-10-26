import qrcode
from io import BytesIO

def create_QR_code(url, short_url):
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        file_name = f"qr_{short_url}.png"
        return file_name, buffer 
    except Exception as e:
        return '', None