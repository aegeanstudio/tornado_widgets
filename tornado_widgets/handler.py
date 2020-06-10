# -*- coding: UTF-8 -*-

import json
from typing import Optional, Awaitable, Callable

import orjson
import tornado.web
from marshmallow import Schema
from marshmallow.exceptions import MarshmallowError, ValidationError
from raven.contrib.tornado import SentryMixin
from tornado import httputil
from tornado.log import access_log
from tornado.options import options

from tornado_widgets.error import BaseError


class BaseRequestHandlerWithSentry(tornado.web.RequestHandler, SentryMixin):

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def get_sentry_user_info(self):
        try:
            user = self._current_user
        except Exception:
            return dict()
        return dict(
            user=dict(
                is_authenticated=bool(user),
                info=user,
            ),
        )

    def log_exception(self, typ, value, tb):
        rv = super(BaseRequestHandlerWithSentry, self).log_exception(
            typ, value, tb)
        if isinstance(value, BaseError):
            if value.http_status != 500:
                if not value.alert_sentry:
                    return rv
        if isinstance(value, MarshmallowError):
            return rv
        self.captureException(exc_info=(typ, value, tb))
        return rv


class BaseHandler(BaseRequestHandlerWithSentry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = dict()
        self.query_args = dict()
        self.form_data = dict()
        self.json_body = dict()

    def options(self, *args, **kwargs):
        access_log.info('OPTIONS CALLED: %s, %s', args, kwargs)
        self.set_status(204)

    def set_default_headers(self):
        if options.debug:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Methods',
                            'GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH')
            self.set_header('Access-Control-Max-Age', '3600')
            self.set_header('Access-Control-Allow-Headers',
                            'Content-Type, Access-Control-Allow-Headers')

    def get_headers(self):
        return dict(self.request.headers.get_all())

    @staticmethod
    def _decode(*, src, schema: Schema = None):
        result = dict()
        for key, value in src.items():
            result[key] = [item.decode() for item in value]
            if len(result[key]) == 1:
                result[key] = result[key][0]
        if schema:
            return schema.load(result)
        return result

    def get_query_args(self, *, schema: Schema = None) -> dict:
        return self._decode(src=self.request.query_arguments, schema=schema)

    def get_form_data(self, *, schema: Schema = None) -> dict:
        return self._decode(src=self.request.body_arguments, schema=schema)

    def get_json_body(self, schema: Schema = None) -> dict:
        content_type = self.request.headers.get('Content-Type')
        if not content_type:
            return dict()
        if not content_type.startswith('application/json'):
            return dict()
        result = orjson.loads(self.request.body or '{}')
        if schema:
            return schema.load(result)
        return result

    def widgets_get_argument(self, key, casting_func: Callable = None):
        source = ['query_args', 'form_data', 'json_body']
        for s in source:
            value = getattr(self, s, dict()).get(key)
            if value:
                return casting_func(value)


class JSONHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets_extra = dict()
        self.json_result = None

    def set_extra(self, *, extra: dict = None):
        if extra:
            self.widgets_extra.update(**extra)

    def write_json(self, data: dict = None, code: int = None, msg: str = None,
                   http_status: int = 200):
        code = code if code is not None else options.widgets_success_code
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_status(http_status)
        result = dict(code=code, msg=msg, data=data, _extra=self.widgets_extra)
        if (not options.widgets_force_extra) and (not self.widgets_extra):
            del result['_extra']
        self.json_result = result
        result_bytes = orjson.dumps(result).replace(b'</', b'<\\/')
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(result_bytes)

    def write_error(self, status_code: int, **kwargs):
        default = dict(
            code=1000,
            msg='内部错误',
            data=None,
            http_status=status_code,
        )
        if 'exc_info' in kwargs:
            _, err_instance, traceback = kwargs['exc_info']
            if isinstance(err_instance, MarshmallowError):
                self.write_json(
                    code=1001,
                    msg='参数异常',
                    data=(err_instance.normalized_messages()
                          if isinstance(err_instance, ValidationError)
                          else err_instance.args),
                    http_status=400,
                )
            elif isinstance(err_instance, BaseError):
                self.write_json(
                    code=err_instance.code,
                    msg=err_instance.msg,
                    data=err_instance.data,
                    http_status=err_instance.http_status,
                )
            elif isinstance(err_instance, tornado.web.HTTPError):
                self.write_json(
                    code=err_instance.status_code,
                    msg=err_instance.reason or httputil.responses.get(
                        err_instance.status_code, 'Unknown'),
                    data=None,
                    http_status=err_instance.status_code,
                )
            else:
                self.write_json(**default)
        else:
            self.write_json(**default)
        self.finish()


class WidgetsJSON404Handler(JSONHandler):

    def initialize(self, status_code: int) -> None:
        self.set_status(status_code)

    def prepare(self) -> None:
        raise tornado.web.HTTPError(self._status_code)
