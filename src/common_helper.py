import json

from hookah_crm import settings


def build_json_from_dict(data):
    return json.dumps(data, default=lambda value: value.__dict__)


# TODO избавиться - в шаблонах перейти на использование тега -> common_tags->format_date
def date_to_verbose_format(date):
    if date:
        return date.strftime(settings.DATE_FORMAT)
    else:
        return "-"
