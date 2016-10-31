import uuid

from djaio.core.methods import BaseMethod


class TstGetMethodBasic(BaseMethod):

    async def execute(self):
        try:
            self.result = [self.output_model().get_mock_object()]
        except Exception as e:
            self.errors.append({
                'code': 502,
                'message': '{}'.format(e)
            })
        return self.result

class TstGetMethod(BaseMethod):

    async def execute(self):
        try:
            query = """
                SELECT id, name, guid from test_table limit %(limit)s offset %(offset)s;
            """
            _data = await self.app.db.execute('test_db', query, {'limit': self.limit, 'offset': self.offset}, 'select')
            self.result = [dict(d) for d in _data]
        except Exception as e:
            self.errors.append({
                'code': 502,
                'message': '{}'.format(e)
            })
        return self.result


class TstGetDetailMethod(BaseMethod):

    async def execute(self):
        try:
            query = """
                SELECT id, name, guid from test_table where id = %(id)s;
            """
            _data = await self.app.db.execute('test_db', query, {'id': self.params['id']}, 'select')
            self.result = [dict(d) for d in _data]
        except Exception as e:
            self.errors.append({
                'code': 502,
                'message': '{}'.format(e)
            })
        return self.result

class TstPostMethod(BaseMethod):

    async def execute(self):
        try:
            name = self.params['name']
            guid =  uuid.uuid4()
            query = """
            INSERT INTO test_table(name, guid) values(%(name)s, %(guid)s);
            """
            query_get = """
            SELECT id, name, guid from test_table where guid = %(guid)s;
            """
            ins = await self.app.db.execute('test_db', query, {'name': name, 'guid': guid}, 'insert')
            _data = await self.app.db.execute('test_db', query_get, {'guid':guid}, 'select')
            self.result = [dict(d) for d in _data]
        except Exception as e:
            self.errors.append({
                'code': 502,
                'message': '{}'.format(e)
            })
        return self.result


class TstPutMethod(BaseMethod):

    async def execute(self):
        try:
            id = self.params['id']
            name = self.params['name']
            query = """
                    UPDATE test_table set name = %(name)s where id = %(id)s;
                    """
            query_get = """
                        SELECT id, name, guid from test_table where id = %(id)s;
                        """
            upd = await self.app.db.execute('test_db', query, {'name': name, 'id': id}, 'update')
            _data = await self.app.db.execute('test_db', query_get, {'id': id}, 'select')
            self.result = [dict(d) for d in _data]
        except Exception as e:
            self.errors.append({
                'code': 502,
                'message': '{}'.format(e)
            })
        return self.result


class TstDeleteMethod(BaseMethod):

    async def execute(self):
        try:
            id = self.params['id']
            query = """
                                    DELETE from test_table where id = %(id)s;
                                    """
            dlt = await self.app.db.execute('test_db', query, {'id': id}, 'delete')
        except Exception as e:
            self.errors.append({
                'code': 502,
                'message': '{}'.format(e)
            })
        return self.result
