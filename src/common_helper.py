import json


def build_json_from_dict(data):
    return json.dumps(data, default=lambda value: value.__dict__)
