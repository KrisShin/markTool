import json
import os


def save_file(data: dict, file_name: str = 'config'):
    data_in_file = {}
    if os.path.exists(f'./{file_name}'):
        with open(f'./{file_name}', 'r') as fp:
            data_in_file = json.loads(fp.read())
    data_in_file.update(data)
    with open(f'./{file_name}', 'w') as fp:
        fp.write(json.dumps(data_in_file))


def read_file(keys: str | list, file_name: str = 'config'):
    if isinstance(keys, 'str'):
        keys = [keys]
    vals = []
    with open(f'./{file_name}', 'r') as fp:
        data = json.loads(fp.read())
        for key in keys:
            vals.append(data.get(key))
    return vals
