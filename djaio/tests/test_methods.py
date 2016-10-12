#!-*- coding: utf-8 -*-
import os
import aiohttp
import pytest
from aiohttp.test_utils import make_mocked_request

from djaio import Djaio
from ..core.methods import BaseMethod


@pytest.fixture
def create_app(loop):
    djaio = Djaio(custom_init=None, loop=loop)
    return djaio.app


async def test_from_request(create_app):
    method = BaseMethod()

    req = make_mocked_request('GET', '/', )
    await method.from_http(req)
    assert not method.params
