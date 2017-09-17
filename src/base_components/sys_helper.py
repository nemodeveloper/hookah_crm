# -*- coding: utf-8 -*-

import traceback


# Получить трассу вызова методов
def get_stack_trace():
    try:
        return "".join(traceback.format_list(traceback.extract_stack())[10:-2])
    except Exception as e:
        return traceback.format_exc()

