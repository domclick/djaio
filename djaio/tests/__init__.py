import os

from djaio import Djaio
from aiohttp.test_utils import AioHTTPTestCase
from djaio.ext.db import DB
try:
    from djaio.tests.settings.base import TEST_DB as _DB_CONF
except ImportError:
    _DB_CONF = {}


class DjaioAppTestCase(AioHTTPTestCase):

    async def init_db(self):
        db = DB(getattr(self, 'DB_CONF', _DB_CONF))
        self.app.db = db
        await self.app.db.init(loop=self.app.loop)

    def init_routes(self, app):
        pass

    def get_app(self, loop):
        try:
            from app import init_app
            os.environ.setdefault('SETTINGS', 'app.settings.local')
            djaio = Djaio(custom_init=init_app, loop=loop)
            app = djaio.app
            self.DB_CONF = getattr(app.settings, 'TEST_DB', _DB_CONF)
            self.loop = loop
        except Exception as e:
            djaio = Djaio(loop=loop)
            app = djaio.app
        self.init_routes(app)
        return app
