from aiohttp import web
from aiohttp.test_utils import unittest_run_loop
from djaio.core.utils import get_int_or_none
from djaio.core.views import BaseContextmixin, RemoteContextMixin

from djaio.tests import DjaioAppTestCase
from djaio.tests.data.conf import BLNS
from djaio.tests.data.views import (TstDefaultView, TstInputViewBasic, TstInputMobileViewBasic)

class TestBaseViews(DjaioAppTestCase):

    def init_routes(self, app):
        super().init_routes(app)
        app.router.add_get('/test', TstDefaultView)
        app.router.add_get('/test_input', TstInputViewBasic)
        app.router.add_get('/test_input_path/{id}', TstInputViewBasic)
        app.router.add_get('/djaio_app_hello', self.app_hello)
        app.router.add_get('/mobile/test_input', TstInputMobileViewBasic)

    async def app_hello(self, request):
        return web.Response(text='Djaio!')

    @unittest_run_loop
    async def test_app_initial(self):
        request = await self.client.request("GET", "/djaio_app_hello")
        assert request.status == 200
        text = await request.text()
        assert text == 'Djaio!'

    @unittest_run_loop
    async def test_base_content_mixin(self):
        assert await BaseContextmixin().get_context_data() == {}

    @unittest_run_loop
    async def test_remote_content_mixin_get_data_url_map(self):
        assert isinstance(RemoteContextMixin().get_data_url_map(), tuple)

    @unittest_run_loop
    async def test_get_default_view(self):
        req = await self.client.request("GET", "/test")
        text = await req.text()
        assert ('You shall not pass!' in text)

    @unittest_run_loop
    async def test_allowed_methods_default_view(self):
        req_get = await self.client.request("GET", "/test")
        req_post = await self.client.request("POST", "/test")
        req_put = await self.client.request("POST", "/test")
        req_delete = await self.client.request("POST", "/test")
        assert req_get.status == 200
        assert req_post.status == 405
        assert req_put.status == 405
        assert req_delete.status == 405

    @unittest_run_loop
    async def test_get_input_view_bad_request(self):
        req = await self.client.request("GET", "/test_input")
        json = await req.json()
        assert json.get('success') == False
        assert json.get('result') == None
        assert (json.get('errors'))
        assert (json.get('errors')[0].get('message'))
        assert (json.get('errors')[0].get('code') == 400)

    @unittest_run_loop
    async def test_get_input_view_valid_request(self):
        req = await self.client.request("GET", "/test_input?id=1")
        json = await req.json()
        assert json.get('success') == True

    @unittest_run_loop
    async def test_get_input_view_bad_request_path(self):
        req = await self.client.request("GET", "/test_input_path/")
        assert (req.status == 404)

    @unittest_run_loop
    async def test_get_input_view_valid_request_path(self):
        req = await self.client.request("GET", "/test_input_path/1")
        json = await req.json()
        assert json.get('success') == True

    @unittest_run_loop
    async def test_get_input_view_blns_request(self):
        for i, q in enumerate(BLNS):
            if get_int_or_none(q) == None and '#' not in q:
                query_string = '/test_input?id={}'.format(q)
                req = await self.client.request("GET", query_string)
                req.close()
                assert (req.status == 400)

    @unittest_run_loop
    async def test_get_input_view_blns_request_path(self):
        for i, q in enumerate(BLNS):
            if get_int_or_none(q) == None and '#' not in q:
                query_string = '/test_input_path/{}'.format(q)
                req = await self.client.request("GET", query_string)
                req.close()
                assert (req.status == 400 or req.status == 404)

    @unittest_run_loop
    async def test_get_input_mobile_view_bad_request(self):
        req = await self.client.request("GET", "/mobile/test_input")
        json = await req.json()
        assert not json.get('data')
        assert json.get('code') == 400
        assert json.get('error')

    @unittest_run_loop
    async def test_get_input_mobile_view_valid_request(self):
        req = await self.client.request("GET", "/mobile/test_input?id=1")
        json = await req.json()
        assert json.get('code') == 0
        assert json.get('data')