# -*- coding: UTF-8 -*-

from databases.core import Connection

from tornado_widgets.utils import fix_utc


class MySQLBaseModel(object):

    _table: str = ''
    _fields: tuple = ()

    def __init__(self, id_, is_deleted, create_time, update_time):
        self.id_ = id_
        self._is_deleted = is_deleted
        self.create_time = create_time
        self.update_time = update_time

    @property
    def is_deleted(self):
        return bool(self._is_deleted)

    def __repr__(self):
        return '<{class_name}({props})>'.format(
            class_name=self.__class__.__name__,
            props=','.join(
                ['{}={}'.format(k, v) for k, v in self.__dict__.items()]))

    @classmethod
    @fix_utc
    async def get(cls, *, db: Connection, id_):
        sql = (f'SELECT {", ".join(cls._fields)} FROM {cls._table} '
               f'WHERE id = :id_')
        args = dict(id_=id_)
        result = await db.fetch_one(query=sql, values=args)
        return cls(*result) if result else None

    @classmethod
    async def delete_by_id(cls, *, db: Connection, id_, force: bool = False):
        if force:
            sql = f'DELETE FROM {cls._table} WHERE id=:id_'
            args = dict(id_=id_)
        else:
            sql = (f'UPDATE {cls._table} SET is_deleted=:is_deleted '
                   f'WHERE id=:id_')
            args = dict(is_deleted=True, id_=id_)
        return await db.execute(query=sql, values=args)

    async def delete_self(self, *, db: Connection, force: bool = False):
        if force:
            sql = f'DELETE FROM {self._table} WHERE id=:id_'
            args = dict(id_=self.id_)
        else:
            sql = (f'UPDATE {self._table} SET is_deleted=:is_deleted '
                   f'WHERE id=:id_')
            args = dict(is_deleted=True, id_=self.id_)
        return await db.execute(query=sql, values=args)
