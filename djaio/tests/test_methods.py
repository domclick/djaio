#!-*- coding: utf-8 -*-
import os
import aiohttp
import pytest
from aiohttp.test_utils import make_mocked_request

from djaio import Djaio
from app import init_app
from ..core.methods import BaseMethod


@pytest.fixture
def create_app(loop):
    os.environ.setdefault('SETTINGS', 'app.settings.test')
    djaio = Djaio(custom_init=init_app, loop=loop)
    #djaio = Djaio(loop)
    return djaio.app


async def test_from_request():
    method = BaseMethod()
    with pytest.raises(aiohttp.web_exceptions.HTTPBadRequest):
        await method.from_http(None)

    req = make_mocked_request('GET', '/', )
    await method.from_http(req)
    assert not method.params
