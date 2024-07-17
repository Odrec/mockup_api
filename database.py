import json
from pathlib import Path

DATA_PATH = Path("data/quotas.json")


def read_data():
    if DATA_PATH.exists():
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    return {"quotas": []}


def write_data(data):
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)


def get_all_quotas():
    return read_data()['quotas']


def update_quotas(new_quotas):
    data = read_data()
    data['quotas'] = new_quotas
    write_data(data)
