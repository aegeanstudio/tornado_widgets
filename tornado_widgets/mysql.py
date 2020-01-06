# -*- coding: UTF-8 -*-

import functools

from databases import Database


def create_connection_pool(*, url, min_size, max_size, **kwargs):
    kwargs.update(dict(min_size=min_size, max_size=max_size))
    return Database(url=url, **kwargs)


def generate_transaction_decorator(*, pool: Database):

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with pool.connection() as connection:
                kwargs['db'] = connection
                async with connection.transaction():
                    return await func(*args, **kwargs)
        return wrapper
    return decorator
