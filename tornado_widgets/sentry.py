# -*- coding: UTF-8 -*-

import weakref
from typing import Any, Optional

from marshmallow.exceptions import MarshmallowError
from sentry_sdk.hub import Hub
from sentry_sdk.integrations.tornado import (
    _make_event_processor, _capture_exception)
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.logging import ignore_logger
from tornado.web import RequestHandler

from tornado_widgets.error import BaseError


class TornadoWidgetsIntegration(Integration):

    identifier = 'tornado'

    @staticmethod
    def setup_once() -> None:

        ignore_logger('tornado.access')

        old_execute = RequestHandler._execute  # type: ignore

        async def sentry_execute_request_handler(self, *args, **kwargs):
            # type: (Any, *Any, **Any) -> Any
            hub = Hub.current

            weak_handler = weakref.ref(self)

            with Hub(hub) as hub:
                with hub.configure_scope() as scope:
                    scope.clear_breadcrumbs()
                    processor = _make_event_processor(weak_handler)
                    scope.add_event_processor(processor)
                return await old_execute(self, *args, **kwargs)

        RequestHandler._execute = sentry_execute_request_handler
        old_log_exception = RequestHandler.log_exception

        def sentry_log_exception(self, ty, value, tb, *args, **kwargs):
            # type: (Any, type, BaseException, Any, *Any, **Any) -> Optional[Any]   # NOQA
            if issubclass(ty, BaseError):
                if value.alert_sentry:
                    _capture_exception(ty, value, tb)
            elif not issubclass(ty, MarshmallowError):
                _capture_exception(ty, value, tb)
            return old_log_exception(self, ty, value, tb)  # type: ignore

        RequestHandler.log_exception = sentry_log_exception  # type: ignore
