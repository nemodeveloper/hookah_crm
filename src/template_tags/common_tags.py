from django.template.defaulttags import register

from hookah_crm import settings


@register.filter(name='format_date')
def format_date(value, arg):
    return value.strftime(arg if arg else settings.DATE_FORMAT)


# Округлить число
# arg - число знаков после запятой
@register.filter(name='round_number')
def round_number(value, arg):
    return round(value, int(arg) if arg else 0)


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
