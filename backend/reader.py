import json

FILEPATH = './temp_db.json'


def read_file():
    data = None
    with open(FILEPATH, 'r') as fp:
        try:
            data = json.load(fp) if fp else None
        except Exception:
            data = None
    return data if data else {}


def write_file(data):
    with open(FILEPATH, 'w+') as fp:
        json.dump(data, fp, indent=4)

