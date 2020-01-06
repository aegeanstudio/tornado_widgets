# -*- coding: UTF-8 -*-

import tornado.web
import tornado.ioloop
from apispec import APISpec
from raven.contrib.tornado import AsyncSentryClient

from tornado_widgets.router import Router


class App(object):

    def __init__(self, *, name: str, config: object = None,
                 settings: dict = None):
        self.name = name
        self.config = config
        self.loop = None
        self.app = None
        self.loggers = []
        self.settings = dict(
            autoreload=config.DEBUG,
            gzip=True,
        )
        if settings:
            self.settings.update(**settings)
        self.prepare_funcs = []
        self.routers = []
        self.spec = None

    def register_logger(self, *, logger_class):
        self.loggers.append(logger_class)

    def register_router(self, *, route_obj: Router):
        self.routers.append(route_obj)

    def register_spec(self, *, spec_obj: APISpec):
        self.spec = spec_obj

    def register_prepare_func(self, *, func):
        self.prepare_funcs.append(func)

    def log(self, *args, **kwargs):
        pass

    @property
    def _route_as_list(self):
        result = []
        for item in self.routers:
            result.extend([(k, v) for k, v in item.route_mapper.items()])
        return result

    def _gen_swagger_handler(self, routes):
        for r in routes:
            self.spec.path(urlspec=r)

        spec = self.spec
        from tornado_widgets.handler import JSONHandler

        class SwaggerHandler(JSONHandler):
            async def get(self):
                print(spec.to_dict())
                self.write(spec.to_dict())
        return SwaggerHandler

    def run(self, *, use_uvloop: bool = True):
        if use_uvloop:
            import asyncio
            import uvloop
            asyncio.set_event_loop_policy(policy=uvloop.EventLoopPolicy())
        self.loop = tornado.ioloop.IOLoop.current()
        for item in self.prepare_funcs:
            self.loop.run_sync(func=item)
        route_as_list = self._route_as_list
        if self.config.DEBUG and self.spec:
            route_as_list.append(
                ('/swagger.json',
                 self._gen_swagger_handler(routes=route_as_list)))
        self.app = tornado.web.Application(
            handlers=route_as_list, **self.settings)
        if hasattr(self.config, 'SENTRY_DSN'):
            self.app.sentry_client = AsyncSentryClient(
                dsn=self.config.SENTRY_DSN)
        self.app.listen(port=self.config.PORT)
        self.loop.start()
