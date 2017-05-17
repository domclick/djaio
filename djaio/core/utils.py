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
    try:
        return int(int(re.sub(r'(\D*)$', '', value)))
    except (TypeError, ValueError):
        return None
