# -*- coding: UTF-8 -*-

import functools

from gino import create_engine, Gino
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql import sqltypes

from tornado_widgets.utils import PrintMixin


DEFAULT_ZERO_DATETIME = '1970-01-01T00:00:00.000000+00:00'


def create_postgres(*, url, **kwargs):
    from sqlalchemy import create_engine
    return Gino(bind=create_engine(url, **kwargs))


def generate_asyncpg_engine_setter(*, db: Gino, url, pool_size, **kwargs):
    async def _set():
        db.bind = await create_engine(
            url, min_size=pool_size, max_size=pool_size, **kwargs)
    return _set


def create_base_model(*, db: Gino):

    from sqlalchemy import func

    class _WidgetsPostgresBaseModel(db.Model, PrintMixin):

        __abstract__ = True

        id_ = Column(
            name='id', type_=sqltypes.BigInteger(), primary_key=True,
            nullable=False, autoincrement=True)
        is_deleted = Column(
            name='is_deleted', type_=sqltypes.Boolean(), nullable=False,
            index=True, server_default='f')
        create_time = Column(
            name='create_time', type_=sqltypes.DateTime(timezone=True),
            nullable=False, index=True,
            server_default=text('CURRENT_TIMESTAMP'))
        update_time = Column(
            name='update_time', type_=sqltypes.DateTime(timezone=True),
            nullable=False, index=True,
            server_default=text('CURRENT_TIMESTAMP'),
            server_onupdate=text('CURRENT_TIMESTAMP'))

        def __init__(self, *args, **kwargs):
            super(_WidgetsPostgresBaseModel, self).__init__(*args, **kwargs)

        def __repr__(self):
            return '<{class_name}({props})>'.format(
                class_name=self.__class__.__name__,
                props=','.join(
                    ['{}={}'.format(k, v)
                     for k, v in self.__values__.items()]))

    return _WidgetsPostgresBaseModel


def generate_transaction_decorator(*, db: Gino):

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with db.acquire() as connection:
                # kwargs['db'] = connection
                async with connection.transaction():
                    return await func(*args, **kwargs)
        return wrapper
    return decorator
