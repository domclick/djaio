#!-*- coding: utf-8 -*-
import re
import asyncio


async def gather_map(map, coro, *args, **kwargs):
    _keys = []
    _coros = []
    for key, value in map:
        _keys.append(key)
        _coros.append(coro(value, *args, **kwargs))
    _results = await asyncio.gather(*_coros)
    return zip(_keys, _results)


def get_int_or_none(value):
    """
    >>> get_int_or_none(123)
    123
    >>> get_int_or_none('123asda')
    123
    """
    if isinstance(value, int):
        return value
    try:
        return int(re.sub(r'^(\d+)(.*)$', r'\1', value))
    except (TypeError, ValueError):
        return None
