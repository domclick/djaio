#!-*- coding: utf-8 -*-
import asyncio

from psycopg2 import errorcodes


async def gather_map(map, coro, *args, **kwargs):
    _keys = []
    _coros = []
    for key, value in map:
        _keys.append(key)
        _coros.append(coro(value, *args, **kwargs))
    _results = await asyncio.gather(*_coros)
    return zip(_keys, _results)


def get_int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_pg_error(code):
    try:
        return errorcodes.lookup(code)
    except KeyError:
        return 'Unknown error'
