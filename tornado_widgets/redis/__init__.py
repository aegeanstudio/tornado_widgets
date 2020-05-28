# -*- coding: UTF-8 -*-

import functools
from typing import Dict

from aioredis.connection import RedisConnection
from aioredis.commands import Redis
from aioredis.pool import ConnectionsPool
from aioredis.util import parse_url


class WidgetsRedisConnectionsPool(ConnectionsPool):

    async def connect(self):
        try:
            await self._fill_free(override_min=False)
        except Exception:
            self.close()
            await self.wait_closed()
            raise


def widgets_create_pool(
        *, address, db=None, password=None, ssl=None, encoding=None, size=8,
        parser=None, create_connection_timeout=None):
    address, options = parse_url(address)
    db = options.setdefault('db', db)
    password = options.setdefault('password', password)
    encoding = options.setdefault('encoding', encoding)
    create_connection_timeout = options.setdefault(
        'timeout', create_connection_timeout)
    if 'ssl' in options:
        assert options['ssl'] or (not options['ssl'] and not ssl), (
            'Conflicting ssl options are set', options['ssl'], ssl)
        ssl = ssl or options['ssl']

    return WidgetsRedisConnectionsPool(
        address=address, db=db, password=password, encoding=encoding,
        minsize=size, maxsize=size, ssl=ssl, parser=parser,
        create_connection_timeout=create_connection_timeout,
        connection_cls=RedisConnection)


def generate_redis_decorator(*, pool_mapping: Dict[str, ConnectionsPool]):

    def redis_decorator(*, key: str):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                async with pool_mapping[key].get() as connection:
                    kwargs['redis'] = Redis(connection)
                    return await func(*args, **kwargs)
            return wrapper
        return decorator
    return redis_decorator
