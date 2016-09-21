import json

from hookah_crm import settings


def build_json_from_dict(data):
    return json.dumps(data, default=lambda value: value.__dict__)


def date_to_verbose_format(date):
    if date:
        return date.strftime(settings.DATE_FORMAT)
    else:
        return "-"
