# -*- coding: utf-8 -*-
import warnings
from typing import List, Dict, Union, Optional

import aiopg
from psycopg2.extras import DictCursor, DictRow


class DB:
    def __init__(self, config: Dict):
        self.config = config
        self.dbs = {}

    async def init(self, minsize=1, maxsize=10, timeout=5, loop=None):
        for _key, _creds in self.config.items():
            self.dbs[_key] = {}
            for _role, _dsn in _creds.items():
                self.dbs[_key][_role] = await aiopg.create_pool(
                    _dsn, minsize=minsize, maxsize=maxsize, timeout=timeout, loop=loop
                )

    async def shutdown(self, app):
        # close connections

        for k, db in self.dbs.items():
            for role, item in db.items():
                if item is not None:
                    item.close()

        for k, db in self.dbs.items():
            for role, item in db.items():
                if item is not None:
                    await item.wait_closed()

    async def execute(self, db_name: str, query: str, values: List, _type: str):
        """
        Execute SQL query in connection pool
        """
        warnings.warn("Use single methods!", DeprecationWarning)

        if _type not in ('select', 'insert', 'update', 'delete'):
            raise RuntimeError(
                'Wrong request type {}'.format(_type)
            )
        if not self.dbs[db_name]['master']:
            raise RuntimeError(
                'db {} master is not initialized'.format(db_name)
            )

        pool = self.dbs[db_name]['master']
        if _type == 'select' and 'slave' in self.dbs[db_name]:
            pool = self.dbs[db_name]['slave']

        async with pool.acquire() as conn:
            async with conn.cursor(cursor_factory=DictCursor) as cursor:
                await cursor.execute(query, values)
                if _type == 'select':
                    data = await cursor.fetchall()
                else:
                    data = cursor.rowcount
        return data

    async def select(self, query: str, values: Union[List, Dict],
                     db_name: str = 'default') -> List[DictRow]:
        return await self._select(query=query, values=values, db_name=db_name)

    async def first(self, query: str, values: Union[List, Dict],
                    db_name: str = 'default') -> Optional[DictRow]:
        return await self._first(query=query, values=values, db_name=db_name)

    async def insert(self, query: str, values: Union[List, Dict],
                     db_name: str = 'default', returning: bool = False):
        return await self._execute(query=query, values=values, db_name=db_name, returning=returning)

    async def update(self, query: str, values: Union[List, Dict],
                     db_name: str = 'default', returning: bool = False):
        return await self._execute(query=query, values=values, db_name=db_name, returning=returning)

    async def delete(self, query: str, values: Union[List, Dict], db_name: str = 'default'):
        return await self._execute(query=query, values=values, db_name=db_name)

    async def _execute(self, query: str, values: Union[List, Dict], db_name: str = 'default',
                       returning: bool = False):
        pool = self.dbs[db_name]['master']
        if pool is None:
            raise RuntimeError('db {} master is not initialized'.format(db_name))

        async with pool.acquire() as conn:
            async with conn.cursor(cursor_factory=DictCursor) as cursor:
                await cursor.execute(query, values)
                if returning:
                    return await cursor.fetchone()
                else:
                    return cursor.rowcount

    async def _select(self, query: str, values: Union[List, Dict], db_name: str = 'default'):
        dbs = self.dbs[db_name]
        pool = dbs.get('slave') or dbs.get('master')
        if pool is None:
            raise RuntimeError('db {} master is not initialized'.format(db_name))

        async with pool.acquire() as conn:
            async with conn.cursor(cursor_factory=DictCursor) as cursor:
                await cursor.execute(query, values)
                return await cursor.fetchall()

    async def _first(self, query: str, values: Union[List, Dict], db_name: str = 'default'):
        dbs = self.dbs[db_name]
        pool = dbs.get('slave') or dbs.get('master')
        if pool is None:
            raise RuntimeError('db {} master is not initialized'.format(db_name))

        async with pool.acquire() as conn:
            async with conn.cursor(cursor_factory=DictCursor) as cursor:
                await cursor.execute(query, values)
                return await cursor.fetchone()


def setup(app):
    _minsize = getattr(app.settings, 'DB_POOL_MINSIZE', 1)
    _maxsize = getattr(app.settings, 'DB_POOL_MAXSIZE', 10)
    _timeout = getattr(app.settings, 'DB_TIMEOUT', 5)
    db = DB(app.settings.DATABASE)
    app.loop.run_until_complete(db.init(minsize=_minsize, maxsize=_maxsize, timeout=_timeout))
    app.db = db
    app.on_cleanup.append(db.shutdown)
