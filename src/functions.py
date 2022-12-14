import qrcode
from src.server_apis import WebServerManager

from src.settings import BASE_URL, RULES


def generate_qr_code():
    if WebServerManager.test_server() != 200:
        return False
    img = qrcode.make(f'{BASE_URL}/works/')
    img.save("server_qr_code.png")
    return True


def get_total_score(score, score_weight, work, rule_total_mapping):
    total = score * score_weight
    for key, val in work.items():
        if key not in RULES:
            continue
        total += RULES[key] * (val / rule_total_mapping[key])
    return total


if __name__ == '__main__':
    generate_qr_code()
