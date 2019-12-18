# -*- coding: UTF-8 -*-

from typing import Optional, Awaitable

import tornado.web
from marshmallow import Schema
from marshmallow.exceptions import MarshmallowError, ValidationError
from raven.contrib.tornado import SentryMixin

from tornado_widgets.error import BaseError


class BaseRequestHandlerWithSentry(tornado.web.RequestHandler, SentryMixin):

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        raise NotImplemented

    def get_sentry_user_info(self):
        try:
            user = self._current_user
        except Exception as e:
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


class JSONHandler(BaseRequestHandlerWithSentry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write_json(self, data=None, code: int=0, msg: str=None,
                   http_status: int=200, schema: Schema=None):
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_status(http_status)
        if schema:
            data = schema.dump(data)
        self.write(dict(code=code, msg=msg, data=data))

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
                    data=err_instance.normalized_messages() if isinstance(err_instance, ValidationError) else err_instance.args,
                    http_status=400,
                )
            elif isinstance(err_instance, BaseError):
                self.write_json(
                    code=err_instance.code,
                    msg=err_instance.msg,
                    data=err_instance.data,
                    http_status=err_instance.http_status,
                )
            else:
                self.write_json(**default)
        else:
            self.write_json(**default)
        self.finish()
