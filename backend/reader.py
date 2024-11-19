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


def get_user(id):
    data = read_file(FILEPATH)
    return data.get(id)


def update_user(id, val):
    data = read_file(FILEPATH)
    data[id] = val
    write_file(FILEPATH, data)
    