# -*- coding: UTF-8 -*-


class Router(object):

    def __init__(self, *, prefix: str = ''):
        self.prefix = prefix
        self.route_mapper = dict()

    def route(self, *, route):
        def decorator(handler_cls):
            if route in self.route_mapper:
                raise BaseException('Duplicated Route!')
            self.route_mapper[self.prefix + route] = handler_cls
            return handler_cls
        return decorator
