# -*- coding: UTF-8 -*-

import pkgutil
from importlib import import_module

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin

from tornado_widgets.router import Router

router = Router(prefix='/api/v1')
spec = APISpec(
    title='APIDocs', version='0.0.1', openapi_version='3.0.0',
    plugins=[MarshmallowPlugin(), TornadoPlugin()])

for _, name, _ in pkgutil.iter_modules(__path__):
    import_module(f'{__package__}.{name}')
