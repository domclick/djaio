# -*- coding: utf-8 -*-
import json

from aiohttp.hdrs import (
    METH_GET,
    METH_POST,
    METH_PUT,
    METH_DELETE
)
from aiohttp import web, MultiDictProxy
from djaio.core.exceptions import BadRequestException
from djaio.core.models import NullInput, NullOutput

from djaio.core.utils import get_int_or_none
from schematics.exceptions import ModelConversionError, ConversionError, DataError, ValidationError


class BaseMethod(object):
    def __init__(self, input_model=NullInput, output_model=NullOutput, description=None):
        self.result = None
        self.input_model = input_model
        self.output_model = output_model
        self.total = None
        self.success = None
        self.errors = None
        self.params = None
        self.output = None
        self.pagination = None
        self.limit = None
        self.offset = None
        self.app = None
        self.settings = None
        self.description = description

    def process_request(self, multi):
        #Override it for your purposes
        params = {}
        # Here we convert a MultiDict to simple python dict.py
        if isinstance(multi, MultiDictProxy):
            for k in set(multi.keys()):
                v = multi.getall(k)
                params[k] = v if len(v) > 1 else v[0]
        elif isinstance(multi, dict):
            params = multi
        else:
            raise BadRequestException(message='request params must be a dict-like object')
        return params

    async def from_http(self, request):
        self.total = None
        self.success = None
        self.errors = []
        self.params = None
        self.output = None
        self.pagination = None
        self.limit = None
        self.offset = None
        if not isinstance(request, web.Request):
            raise web.HTTPBadRequest()
        try:
            req_params = {}
            # if GET or DELETE we read a query params
            if request.method in (METH_GET, METH_DELETE):
                req_params = self.process_request(request.GET)
            # else we read a POST-data
            elif request.method in (METH_PUT, METH_POST):
                try:
                    req_params = self.process_request(await request.json())
                except (ValueError, TypeError):
                    req_params = self.process_request(await request.post())

            # Here we add or owerride params by PATH-params.
            # If it exist
            if request.match_info:
                req_params.update(request.match_info.copy())

            self.limit = get_int_or_none(request.headers.get('X-Limit')) or \
                         get_int_or_none(req_params.pop('limit', None)) or \
                         get_int_or_none(request.app.settings.LIMIT)
            self.offset = get_int_or_none(request.headers.get('X-Offset')) or \
                          get_int_or_none(req_params.pop('offset', None)) or \
                          get_int_or_none(request.app.settings.OFFSET)

            params = self.input_model(req_params, strict=False)
            params.validate()
            self.params = params.to_primitive()
        except (ModelConversionError, ConversionError, DataError) as exc:
            errors = []
            if isinstance(exc.messages, list):
                errors = [x.summary for x in exc.messages]
            else:
                for k, v in exc.messages.items():
                    sub_errors = {}
                    if isinstance(v, dict):
                        for sub_k, error in v.items():
                            if isinstance(error, ConversionError) or isinstance(error, ValidationError):
                                sub_errors[sub_k] = [x.summary for x in error.messages]
                        errors.append({k: sub_errors})

                    elif isinstance(v, ConversionError) or isinstance(v, ValidationError):
                        errors.append({k: [x.summary for x in v.messages]})

                    elif isinstance(v, list):
                        errors.append({k: [x.summary for x in v]})
                    elif isinstance(v, str):
                        errors.append({k: v})
            raise BadRequestException(message=errors)

        self.result = []
        self.app = request.app
        self.settings = request.app.settings

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
            'success': not self.errors
        }
        if not self.errors:
            if type(self.result) in (list, tuple) or isinstance(self.result, map):
                self.output['result'] = [self.output_model(x).to_primitive() for x in self.result]
            elif type(self.result) == dict:
                self.output['result'] = self.output_model(self.result).to_primitive()
            else:
                self.output['result'] = self.result
        else:
            self.output.update({'errors': self.errors})
        pagination = self.get_pagination()
        if pagination:
            self.output.update({'pagination': pagination})
        return self.output
