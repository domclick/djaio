import json

from djaio.core import exceptions
from djaio.core.methods import BaseMethod
from djaio.ext.utils import BaseJsonEncoder

PGCODE_EXCEPIONS = {
    '23505': exceptions.ObjectAlreadyExistException(),
    '23502': exceptions.BadRequestException(message='Wrong data types or values'),
}


class BaseDetailMethod(BaseMethod):
    db_name = 'default'
    table_name = None
    to_json = []
    query = None

    def _to_json(self):
        for p in self.to_json:
            self.params[p] = (json.dumps(self.params.get(p, []), cls=BaseJsonEncoder))

    def _prepare_query(self):
        if not self.table_name:
            raise BaseException('You must set a table_name to execute query!')
        if not self.query:
            raise BaseException('You must set a query!')
        self._to_json()


class BaseDetailGetMethod(BaseDetailMethod):
    query = """SELECT {keys} FROM {table_name} WHERE id = %(id)s AND is_deleted = FALSE LIMIT 1;"""

    def _prepare_query(self):
        super()._prepare_query()
        return self.query.format(
            table_name=self.table_name,
            id=self.params.get('id', 0),
            keys=','.join(self.output_model.fields)
        )

    async def execute(self):
        query = self._prepare_query()
        cur = await self.app.db.select(query, {'id': self.params.get('id', 0)}, db_name=self.db_name)
        if not len(cur):
            raise exceptions.ObjectNotFoundException(_id=self.params.get('id', None))
        return {k: cur[0].get(k) for k in self.output_model.fields}


class BaseDetailDeleteMethod(BaseDetailMethod):
    query = """UPDATE {table_name} SET is_deleted = True, updated = now() WHERE id = %(id)s"""

    def _prepare_query(self):
        super()._prepare_query()
        return self.query.format(
            table_name=self.table_name,
        )

    async def execute(self):
        query = self._prepare_query()
        try:
            cur = await self.app.db.delete(query, {'id': self.params.get('id', 0)}, db_name=self.db_name)
        except Exception as e:
            pgcode = getattr(e, 'pgcode', None)
            if PGCODE_EXCEPIONS.get(pgcode):
                raise PGCODE_EXCEPIONS[pgcode]
            raise e
        if not int(cur):
            raise exceptions.ObjectNotFoundException(_id=id)
        return {}


class BaseDetailPutMethod(BaseDetailMethod):
    query = """UPDATE {table_name} SET {updates}, updated=now() WHERE id=%(id)s AND is_deleted = False"""

    def _prepare_query(self):
        super()._prepare_query()
        return self.query.format(
            table_name=self.table_name,
            updates=','.join(["{}=%({})s".format(k, k) for k in self.params]),
        )

    async def execute(self):
        query = self._prepare_query()
        try:
            cur = await self.app.db.update(query, self.params, db_name=self.db_name)
        except Exception as e:
            pgcode = getattr(e, 'pgcode', None)
            if PGCODE_EXCEPIONS.get(pgcode):
                raise PGCODE_EXCEPIONS[pgcode]
            raise e
        if not cur:
            raise exceptions.ObjectNotFoundException(_id=self.params['id'])

        return {
            'id': self.params['id'],
        }


class BaseDetailPostMethod(BaseDetailMethod):
    query = """INSERT INTO {table_name} ({keys}, created, updated) VALUES ({values}, now(), now()) RETURNING id;"""

    def _prepare_query(self):
        super()._prepare_query()
        return self.query.format(
            table_name=self.table_name,
            keys=','.join(self.params.keys()),
            values=','.join('%({})s'.format(k) for k in self.params.keys())
        )

    async def execute(self):
        query = self._prepare_query()
        try:
            cur = await self.app.db.insert(query, self.params, returning=True, db_name=self.db_name)
        except Exception as e:
            pgcode = getattr(e, 'pgcode', None)
            if PGCODE_EXCEPIONS.get(pgcode):
                raise PGCODE_EXCEPIONS[pgcode]
            raise e

        if not len(cur):
            raise exceptions.BadRequestException()

        return {
            'id': cur[0],
        }


class BaseGetByOneKeyMethod(BaseDetailMethod):
    key = None

    query = """SELECT {keys} FROM {table_name} WHERE {key} = %({key})s AND is_deleted = FALSE LIMIT 1;"""

    def _prepare_query(self):
        super()._prepare_query()
        if not self.key:
            raise BaseException('You must set the parameter to execute query!')
        return self.query.format(
            table_name=self.table_name,
            key=self.key,
            keys=','.join(self.output_model.fields)
        )

    async def execute(self):
        query = self._prepare_query()
        cur = await self.app.db.select(query, {self.key: self.params[self.key]}, db_name=self.db_name)
        if not len(cur):
            raise exceptions.ObjectNotFoundException(_id=self.params[self.key])
        return {k: cur[0].get(k) for k in self.output_model.fields}


class BaseDetailGetSingleMethod(BaseDetailGetMethod):
    query = """select {keys} from {table_name} where id = {id} and is_deleted = FALSE LIMIT 1;"""

    async def execute(self):
        query = self._prepare_query()
        cur = await self.app.db.select(query, {}, db_name=self.db_name)
        if not len(cur):
            raise exceptions.ObjectNotFoundException(_id=self.params.get('id', None), db_name=self.db_name)
        return {k: cur[0].get(k) for k in self.output_model.fields}
