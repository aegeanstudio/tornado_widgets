# -*- coding: UTF-8 -*-

from collections import namedtuple

ErrorMeta = namedtuple('Error',
                       ['code', 'msg', 'data', 'http_status', 'alert_sentry'])


class BaseError(Exception):
    """ 业务异常基类 """

    _error = ErrorMeta(1000, '内部错误', None, 500, True)

    def __init__(self, code: int = None, msg: str = None, data: dict = None,
                 http_status: int = None, alert_sentry: bool = False):
        super(BaseError, self).__init__()
        self.code = code or self._error.code
        self.msg = msg or self._error.msg
        self.data = data or self._error.data
        self.http_status = http_status or self._error.http_status
        self.alert_sentry = alert_sentry or self._error.alert_sentry
        args = dict(
            code=self.code,
            msg=self.msg,
            data=self.data,
            http_status=self.http_status,
            alert_sentry=self.alert_sentry,
        )
        self.args = (
            '<{e}>'.format(
                e=', '.join(['{}: {}'.format(k, v) for k, v in args.items()]),
            ),
        )

    def __repr__(self):
        return '<{class_name}({props})>'.format(
            class_name=self.__class__.__name__,
            props=','.join(
                ['{}={}'.format(k, f'"{v}"' if isinstance(v, str) else v)
                 for k, v in self.__dict__.items()]))
