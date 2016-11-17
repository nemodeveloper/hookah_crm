from random import random

from django import template
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


# TODO доделать радомную генерацию в шаблонах
# @register.tag(name="random_gen")
# def random_gen(parser, token):
#     items = []
#     bits = token.split_contents()
#     for item in bits:
#         items.append(item)
#     return RandomGenNode(items[1:])
#
#
# class RandomGenNode(template.Node):
#     def __init__(self, items):
#         self.items = []
#         for item in items:
#             self.items.append(item)
#
#     def render(self, context):
#         arg1 = self.items[0]
#         arg2 = self.items[1]
#         if "hash" in self.items:
#             result = os.urandom(16).encode('hex')
#         elif "float" in self.items:
#             result = random.uniform(int(arg1), int(arg2))
#         elif not self.items:
#             result = random.random()
#         else:
#             result = random.randint(int(arg1), int(arg2))
#         return result
