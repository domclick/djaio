import asyncio

async def gather_map(map, coro, *args, **kwargs):
    _keys = []
    _coros = []
    for key, value in map:
        _keys.append(key)
        _coros.append(coro(value, *args, **kwargs))
    _results = await asyncio.gather(*_coros)
    return zip(_keys, _results)
