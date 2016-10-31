import psycopg2
import pytest

from aiohttp.test_utils import unittest_run_loop

from djaio.tests import DjaioAppTestCase
from djaio.tests.data.conf import BLNS

class TestBaseDBExt(DjaioAppTestCase):

    @unittest_run_loop
    async def test_base_db_ext_empty_db_valid_select(self):
        await self.init_db()
        await self.app.db.execute('test_db', 'select 1;', [], 'select')
        assert True

    @unittest_run_loop
    async def test_base_db_ext_empty_db_valid_queries(self):
        await self.init_db()
        await self.app.db.execute('test_db', "INSERT INTO test_table(name) VALUES ('djaio');", [], 'insert')
        await self.app.db.execute('test_db', "UPDATE test_table set name='djaio_new' WHERE name='djaio';", [], 'update')
        await self.app.db.execute('test_db', "DELETE FROM test_table where name='djaio_new';", [], 'delete')
        assert True

    @unittest_run_loop
    async def test_base_db_ext_empty_db_wrong_type(self):
        await self.init_db()
        for t in BLNS:
            try:
                await self.app.db.execute('test_db', 'select 1;', [], t)
            except RuntimeError:
                assert True

    @unittest_run_loop
    async def test_base_db_ext_valid_and_wrong_inserts(self):
        await self.init_db()
        with pytest.raises(psycopg2.ProgrammingError):
            await self.app.db.execute(db_name='test_db', query="""
                    INSERT INTO test_table(name) VALUES ('djaio_boo');
                    INSERT INTO test_table(name1) VALUES ('djaio');
            """, values=[], _type='select')
        bad_val = await self.app.db.execute('test_db', "select * from test_table  where name='djaio_boo';", [], 'select')
        assert bad_val == []
        assert True

    @unittest_run_loop
    async def test_base_db_ext_validate_cursor_data(self):
        await self.init_db()
        await self.app.db.execute('test_db', "INSERT INTO test_table(name) VALUES (%(name)s);", {'name': 'djaio'},
                                  'insert')
        await self.app.db.execute('test_db', "INSERT INTO test_table(name) VALUES (%(name)s);", {'name': 'djaio'},
                                  'insert')
        await self.app.db.execute('test_db', "INSERT INTO test_table(name) VALUES (%(name)s);", {'name': 'djaio'},
                                  'insert')
        await self.app.db.execute('test_db', "INSERT INTO test_table(name) VALUES (%(name)s);", {'name': 'djaio'},
                                  'insert')
        data = await self.app.db.execute('test_db', "SELECT name from test_table where name = %(name)s",
                                         {'name': "djaio"}, 'select')
        assert isinstance(data, list)
        data = list(map(lambda x: {'name':x['name']},data))
        assert isinstance(data[0], dict)
        assert len(data) == 4
        assert data[0].get('name', None) != None
        assert data[1].get('name', None) == 'djaio'
        assert True
        d = await self.app.db.execute('test_db', "DELETE FROM test_table where name like %(name)s;", {'name':'djaio'}, 'delete')
        assert d > 0
