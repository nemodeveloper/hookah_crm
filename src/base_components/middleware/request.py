# -*- coding: utf-8 -*-

from threading import current_thread

from django.utils.deprecation import MiddlewareMixin


_requests = {}


def get_current_request():
    return _requests.get(current_thread().ident, None)


def get_current_user():
    cur_request = get_current_request()
    return cur_request.user if cur_request else None


# Фильтр сохраняет request для вызывающего кода
class RequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        _requests[current_thread().ident] = request

    def process_response(self, request, response):
        # when response is ready, request should be flushed
        _requests.pop(current_thread().ident, None)
        return response

    def process_exception(self, request, exception):
        # if an exception has happened, request should be flushed too
        _requests.pop(current_thread().ident, None)
        raise exception
