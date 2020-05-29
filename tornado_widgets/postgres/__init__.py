# -*- coding: UTF-8 -*-

import functools
from typing import Coroutine

from gino import create_engine, Gino
from gino.dialects.asyncpg import NullPool
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql import sqltypes

from tornado_widgets.utils import PrintMixin


def create_postgres(*, url, **kwargs):
    engine = create_engine(url, pool_class=NullPool, **kwargs)
    if isinstance(engine, Coroutine):
        engine.close()
        return Gino(bind=url)
    return Gino(bind=engine)


async def set_engine(*, db: Gino, url, **kwargs):
    engine = await create_engine(url, pool_class=NullPool, **kwargs)
    db.bind = engine


def create_base_model(*, db: Gino):

    class _WidgetsPostgresBaseModel(db.Model, PrintMixin):

        __abstract__ = True

        id_ = Column(
            name='id', type_=sqltypes.BigInteger(), primary_key=True,
            nullable=False, autoincrement=True)
        _is_deleted = Column(
            name='is_deleted', type_=sqltypes.Boolean(), nullable=False,
            index=True, server_default='f')
        create_time = Column(
            name='create_time', type_=sqltypes.DateTime(timezone=True),
            nullable=False, index=True, server_default='NOW()')
        update_time = Column(
            name='update_time', type_=sqltypes.DateTime(timezone=True),
            nullable=False, index=True, server_default='NOW()',
            server_onupdate='NOW()')

        def __init__(self, *args, **kwargs):
            super(_WidgetsPostgresBaseModel, self).__init__(*args, **kwargs)

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
