import io
import qrcode


def generate_qr_code(payment_url: str) -> io.BytesIO:
    """Генерирует QR-код по ссылке оплаты и возвращает BytesIO."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_url)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    qr_buffer = io.BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer
