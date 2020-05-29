# -*- coding: UTF-8 -*-

import functools
from datetime import datetime
from enum import Enum

from dateutil.tz import tzlocal, tzutc


class PrintMixin(object):

    def __repr__(self):
        return '<{class_name}({props})>'.format(
            class_name=self.__class__.__name__,
            props=','.join(
                ['{}={}'.format(k, v) for k, v in self.__dict__.items()]))


def now_with_tz():
    return datetime.now(tz=tzlocal())


def auto_enum(func):

    defaults = list()
    if func.__defaults__:
        for item in func.__defaults__:
            if isinstance(item, Enum):
                defaults.append(item.value)
                continue
            defaults.append(item)
        func.__defaults__ = tuple(defaults)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        converted_args = list()
        for arg in args:
            if isinstance(arg, Enum):
                converted_args.append(arg.value)
                continue
            converted_args.append(arg)
        for key, value in kwargs.items():
            if isinstance(value, Enum):
                kwargs[key] = value.value
        return func(*converted_args, **kwargs)
    return wrapper


def auto_utc(func):

    defaults = list()
    if func.__defaults__:
        for item in func.__defaults__:
            if isinstance(item, datetime):
                defaults.append(item.astimezone(tz=tzutc()))
            defaults.append(item)
        func.__defaults__ = tuple(defaults)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        converted_args = list()
        for arg in args:
            if isinstance(arg, datetime):
                converted_args.append(arg.astimezone(tz=tzutc()))
                continue
            converted_args.append(arg)
        for key, value in kwargs.items():
            if isinstance(value, datetime):
                kwargs[key] = value.astimezone(tz=tzutc())
        return func(*converted_args, **kwargs)
    return wrapper


def __fix_item(i):
    for key, value in i.__dict__.items():
        if isinstance(value, datetime):
            setattr(i, key,
                    value.replace(tzinfo=tzutc()).astimezone(tz=tzlocal()))
    return i


def fix_utc(func):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        if not result:
            return result
        if isinstance(result, list):
            return [__fix_item(item) for item in result]
        else:
            return __fix_item(result)
    return wrapper
