# -*- coding: UTF-8 -*-

import functools
from datetime import date, datetime
from typing import Type

from apispec import APISpec
from apispec.exceptions import DuplicateComponentNameError
from dateutil.tz import tzlocal
from marshmallow.exceptions import MarshmallowError
from marshmallow.fields import Field, DateTime
from marshmallow.schema import BaseSchema

from tornado_widgets.handler import JSONHandler


def _generate_schema_func(
        *, schema_src_inner: str, schema_object_inner: BaseSchema):
    return lambda handler_obj: getattr(handler_obj, f'get_{schema_src_inner}')(
        schema=schema_object_inner)


def schema(*, query_args: Type[BaseSchema] = None,
           form_data: Type[BaseSchema] = None,
           json_body: Type[BaseSchema] = None,
           res: Type[BaseSchema] = None,
           reg_to: APISpec = None):

    if reg_to:
        for item in (query_args, form_data, json_body, res):
            if item:
                try:
                    reg_to.components.schema(name=item.__name__, schema=item)
                except DuplicateComponentNameError as e:
                    print(e)

    schema_pairs = dict(
        query_args=query_args,
        form_data=form_data,
        json_body=json_body,
    )

    for schema_src, schema_class in schema_pairs.items():
        schema_object = schema_class() if schema_class else None
        schema_pairs[schema_src] = _generate_schema_func(
            schema_src_inner=schema_src, schema_object_inner=schema_object)

    res = res() if res else None

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self: JSONHandler, *args, **kwargs):
            for sch_src, sch_func in schema_pairs.items():
                setattr(self, sch_src, sch_func(self))
            result = await func(self, *args, **kwargs)
            if res:
                result = res.dump(result)
            self.write_json(data=result)
        return wrapper
    return decorator


class EnumField(Field):

    def __init__(self, enum_class, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        self.enum_class = enum_class

    def _serialize(self, value, *args, **kwargs):
        if value is None:
            return None
        try:
            return value.name
        except Exception:
            raise MarshmallowError

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            _value = value
            if isinstance(value, bytes):
                _value = value.decode('utf-8')
            return self.enum_class[_value]
        except Exception:
            raise MarshmallowError


class LocalDateTimeField(DateTime):

    def _serialize(self, value, *args, **kwargs):
        if value is not None:
            if type(value) == date:
                value = datetime(value.year, value.month, value.day,
                                 tzinfo=tzlocal())
            else:
                value = value.replace(microsecond=0)
                if value.tzinfo is None:
                    value = value.astimezone(tz=tzlocal())
        return super(LocalDateTimeField, self)._serialize(
            value, *args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        result = super(LocalDateTimeField, self)._deserialize(
            value, attr, data, **kwargs)
        return result.astimezone(tz=tzlocal())
