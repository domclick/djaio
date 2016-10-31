from aiohttp.test_utils import unittest_run_loop

from djaio.tests import DjaioAppTestCase
from djaio.tests.data.models import TstOutput, TstPostInput
from djaio.tests.data.views import TstInputView, TstInputDetailView


class TestBaseMethod(DjaioAppTestCase):

    def init_routes(self, app):
        super().init_routes(app)
        app.router.add_get('/test_input', TstInputView)
        app.router.add_post('/test_input', TstInputView)

        app.router.add_get('/test_input/{id}', TstInputDetailView)
        app.router.add_delete('/test_input/{id}', TstInputDetailView)
        app.router.add_put('/test_input/{id}', TstInputDetailView)

    @unittest_run_loop
    async def test_bad_post_request(self):
        req = await self.client.post('/test_input')
        assert req.status == 400

    @unittest_run_loop
    async def test_bad_put_request(self):
        req = await self.client.put('/test_input/a')
        assert req.status == 400

    @unittest_run_loop
    async def test_bad_delete_request(self):
        req = await self.client.delete('/test_input/a')
        assert req.status == 400

    @unittest_run_loop
    async def test_valid_post_request(self):
        await self.init_db()
        data = TstPostInput().get_mock_object()
        req = await self.client.post('/test_input', data=data.to_primitive())
        assert req.status == 201 or req.status == 200
        res = await req.json()
        assert res.get('success') == True
        assert TstOutput(res.get('result', [{}])[0]).validate() == None
        return res

    @unittest_run_loop
    async def test_valid_get_request(self):
        await self.init_db()
        req = await self.client.get('/test_input')
        assert req.status == 200
        res = await req.json()
        assert res.get('success') == True
        assert len(res.get('result')) > 0

    @unittest_run_loop
    async def test_valid_get_detail_request(self):
        await self.init_db()
        data = TstPostInput().get_mock_object()
        req = await self.client.post('/test_input', data=data.to_primitive())
        assert req.status == 201 or req.status == 200
        res = await req.json()
        item = res.get('result')[0]['id']
        select_req = await self.client.get('/test_input/{}'.format(item))
        assert select_req.status == 200
        select_res = await select_req.json()
        assert select_res['success'] == True
        assert len(select_res['result']) == 1
        assert TstOutput(select_res.get('result', [{}])[0]).validate() == None

    @unittest_run_loop
    async def test_valid_put_request(self):
        await self.init_db()
        data = TstPostInput().get_mock_object()
        req = await self.client.post('/test_input', data=data.to_primitive())
        assert req.status == 201 or req.status == 200
        res = await req.json()
        item = res.get('result')[0]['id']
        put_data = TstPostInput({'name':'Show me the money', 'id':item})
        put_req = await self.client.put('/test_input/{}'.format(item), data=put_data.to_primitive())
        assert put_req.status == 200
        put_res = await put_req.json()
        assert put_res['success'] == True
        assert len(put_res['result']) == 1
        put_item = put_res.get('result', [{}])[0]
        assert TstOutput(put_item).validate() == None
        assert put_item['name'] == 'Show me the money'

    @unittest_run_loop
    async def test_valid_delete_request(self):
        await self.init_db()
        data = TstPostInput().get_mock_object()
        req = await self.client.post('/test_input', data=data.to_primitive())
        assert req.status == 201 or req.status == 200
        res = await req.json()
        item = res.get('result')[0]['id']
        del_req = await self.client.delete('/test_input/{}'.format(item))
        assert del_req.status == 204

    @unittest_run_loop
    async def test_valid_delete_request(self):
        await self.init_db()
        data = TstPostInput().get_mock_object()
        req = await self.client.post('/test_input', data=data.to_primitive())
        assert req.status == 201 or req.status == 200
        res = await req.json()
        item = res.get('result')[0]['id']
        del_req = await self.client.delete('/test_input/{}'.format(item))
        assert del_req.status == 204
