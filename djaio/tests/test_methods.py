#!-*- coding: utf-8 -*-
import os
import aiohttp
import pytest
import asyncio
from aiohttp.test_utils import make_mocked_request

from djaio import Djaio
from ..core.methods import BaseMethod


@pytest.fixture
def create_app(loop):
    os.environ.setdefault('SETTINGS', 'app.settings.local')
    djaio = Djaio(loop=loop)
    return djaio.app


loop = asyncio.get_event_loop()
app = create_app(loop)


async def test_from_request(test_client, create_app):
    method = BaseMethod()
    with pytest.raises(aiohttp.web_exceptions.HTTPBadRequest):
        await method.from_http(None)

    req = make_mocked_request('GET', '/', )
    await method.from_http(req)
    assert method.params is not None
