import qrcode
from src.server_apis import WebServerManager

from src.settings import BASE_URL


def generate_qr_code():
    if WebServerManager.test_server() != 200:
        return False
    img = qrcode.make(f'{BASE_URL}/works/')
    img.save("server_qr_code.png")
    return True


if __name__ == '__main__':
    generate_qr_code()
