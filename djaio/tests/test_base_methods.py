from aiohttp.test_utils import make_mocked_request, unittest_run_loop
from djaio.core.methods import BaseMethod

from djaio.tests import DjaioAppTestCase

class TestBaseMethod(DjaioAppTestCase):

    @unittest_run_loop
    async def test_from_request(self):
        method = BaseMethod()
        req = make_mocked_request('GET', '/')
        await method.from_http(req)
        assert not method.params

    @unittest_run_loop
    async def test_base_method_process_request(self):
        method = BaseMethod()
        try:
            await method.execute()
        except NotImplementedError:
            assert True

    @unittest_run_loop
    async def test_base_method_params(self):
        method = BaseMethod()
        req = make_mocked_request('GET', '/?power_rangers=GoGo&Chip=1&Chip=2&Deil=3')
        proc_req = method.process_request(multi=req.GET)
        assert isinstance(proc_req, dict)
        assert proc_req == {'Chip': ['1', '2'], 'Deil': '3', 'power_rangers': 'GoGo'}


    @unittest_run_loop
    async def test_base_method_process_request(self):
        method = BaseMethod()
        try:
            await method.get_output()
        except NotImplementedError:
            assert True
