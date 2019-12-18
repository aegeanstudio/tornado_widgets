# -*- coding: UTF-8 -*-

import tornado.web
import tornado.ioloop
from tornado.options import options


class App(object):

    def __init__(self, *, name: str, options_package: str = None,
                 settings: dict = None):
        if options_package:
            __import__(options_package)
        self.name = name
        self.app = None
        self.logger = None
        self.settings = dict(
            autoreload=options.debug,
            gzip=True,
        )
        if settings:
            self.settings.update(**settings)
        self.routes = []

    def config_logger(self, *, logger_class):
        pass

    @property
    def _route_as_list(self):
        result = []
        for item in self.routes:
            result.extend([(k, v) for k, v in item.route_mapper.items()])
        return result

    def run(self, *, use_uvloop: bool = True):
        if use_uvloop:
            import asyncio
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.app = tornado.web.Application(
            handlers=self._route_as_list, **self.settings)
        self.app.listen(options.port)
        tornado.ioloop.IOLoop.current().start()
