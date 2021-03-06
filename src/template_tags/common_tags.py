import os

import binascii
import random
import string

from django.template.defaulttags import register

from hookah_crm import settings


@register.filter(name='format_date')
def format_date(value, arg=''):
    return value.strftime(arg if arg else settings.DATE_FORMAT)


# Округлить число
# arg - число знаков после запятой
@register.filter(name='round_number')
def round_number(value, arg):
    return round(value, int(arg) if arg else 0)


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


# Проверить доступность прав по имени
@register.filter(name='check_perm')
def check_perm(user, perm_key):
    have_perm = False
    if user.is_authenticated:
        if user.is_superuser:
            have_perm = True
        else:
            have_perm = user.has_perm(perm_key)
    return have_perm


@register.simple_tag()
def random_hex(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

