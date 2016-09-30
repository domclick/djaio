# -*- coding: utf-8 -*-
from aiohttp.hdrs import (
    METH_GET,
    METH_POST,
    METH_PUT,
    METH_DELETE
)
from aiohttp import web
from aiohttp.helpers import MultiDict


class BaseMethod(object):
    def __init__(self):
        self.result = None
        self.total = None
        self.success = None
        self.errors = []
        self.params = None
        self.output = None
        self.pagination = None
        self.limit = None
        self.offset = None

    async def from_http(self, request):
        if not isinstance(request, web.Request):
            raise web.HTTPBadRequest()

        if request.method in (METH_GET, METH_DELETE):
            self.params = MultiDict(request.GET)
        elif request.method in (METH_PUT, METH_POST):
            try:
                self.params = MultiDict(await request.json())
            except (ValueError, TypeError):
                self.params = MultiDict(await request.post())

        self.limit = request.headers.get('X-Limit') or \
            request.GET.get('limit') or \
            request.app.settings.LIMIT
        self.offset = request.headers.get('X-Offset') or \
            request.GET.get('offset') or \
            request.app.settings.OFFSET

    async def execute(self):
        raise NotImplementedError('Please override `execute()` method.')

    def get_pagination(self):
        _pagination_object = {
            'total': self.total,
            'limit': self.limit,
            'offset': self.offset
        }
        if not self.total:
            return
        self.pagination = _pagination_object
        return self.pagination

    async def get_output(self):
        self.result = await self.execute()
        self.output = {
            'result': self.result,
            'success': not self.errors
        }
        if self.errors:
            self.output.update({'errors': self.errors})
        pagination = self.get_pagination()
        if pagination:
            self.output.update({'pagination': pagination})
        return self.output