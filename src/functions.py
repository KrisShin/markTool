import qrcode
import csv
from src.server_apis import WebServerManager
from src.settings import BASE_URL, RULES, TABLE_FILE_HEADER, WORKS


def generate_qr_code():
    if WebServerManager.test_server() != 200:
        return False
    path = f'{BASE_URL}/works/'
    img = qrcode.make(path)
    print(f'Server address is: {path}')
    img.save("server_qr_code.png")
    return True


def get_total_score(score, score_weight, work, rule_total_mapping):
    total = score * score_weight
    for key, val in work.items():
        if key not in RULES:
            continue
        total += RULES[key] * (val / rule_total_mapping[key])
    return total


def export_csv():
    header = ['remote IP'] + TABLE_FILE_HEADER
    csvfile = open('./export_data.csv', 'w')
    writer = csv.writer(csvfile)
    writer.writerow(header)
    rows = []
    if not WORKS:
        return False
    for work_name, work_dict in WORKS.items():
        scores = work_dict.get('scores')
        if not scores:
            row = ['', work_name, 0, *[work_dict.get(rule) for rule in RULES], 0]
            rows.append(row)
            continue
        for ip, score in scores:
            row = [
                ip,
                work_name,
                score,
                *[work_dict.get(rule) for rule in RULES],
                work_dict.get('total', 0),
            ]
            rows.append(row)
    writer.writerows(rows)
    csvfile.close()
    return True


if __name__ == '__main__':
    generate_qr_code()
