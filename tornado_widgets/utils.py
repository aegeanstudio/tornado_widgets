# -*- coding: UTF-8 -*-

import functools
from datetime import datetime
from enum import Enum

from dateutil.tz import tzlocal


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
