import pytest
import aiohttp
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from ..core.methods import BaseMethod


@pytest.fixture
def create_app(loop):
    app = web.Application(loop=loop)
    return app


async def test_from_request(test_client, create_app):
    method = BaseMethod()
    with pytest.raises(aiohttp.web_exceptions.HTTPBadRequest):
        await method.from_http(None)

    req = make_mocked_request('GET', '/', )
    await method.from_http(req)
    assert method.params is not None
