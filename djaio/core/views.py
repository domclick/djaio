#!-*- coding: utf-8 -*-
import asyncio
import aiohttp
from aiohttp import web
from aiohttp.hdrs import METH_ALL
import aiohttp_jinja2

from djaio.core.exceptions import ObjectNotFoundException, ObjectAlreadyExistException, BadRequestException
from djaio.core.utils import gather_map


class BaseContextmixin(object):
    async def get_context_data(self, *args, **kwargs):
        context = {}
        return context


class RemoteContextMixin(BaseContextmixin):
    data_url_map = tuple()

    def get_data_url_map(self):
        return self.data_url_map

    async def get_remote_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise web.HTTPBadGateway
                session.close()
                try:
                    return await resp.json() or ''
                except:
                    raise web.HTTPBadGateway

    async def get_context_data(self, *args, **kwargs):
        context = await super(RemoteContextMixin, self).get_context_data(*args, **kwargs)
        context.update(dict(await gather_map(self.get_data_url_map(), self.get_remote_data)))
        return context


class TemplateView(BaseContextmixin, web.View):
    template_name = None

    def get_template_name(self):
        return self.template_name

    async def render(self):
        return aiohttp_jinja2.render_template(
            self.get_template_name(),
            self.request,
            self.get_context_data()
        )

    async def get(self):
        body = await self.render()
        return body


class JsonView(web.View):
    get_method = None
    post_method = None
    put_method = None
    delete_method = None

    _response = None
    location_url_name = None

    def _set_location_to_response(self, resp):
        result = self._response.get('result')
        if result and len(result) > 0:
            resp.headers.add('Location', self.reverse_url(self.location_url_name, parts=result[0]))

        return resp

    def reverse_url(self, namespace:str, parts:dict=None, query:dict=None):
        return self.request.app.router[namespace].url(parts=parts, query=query)

    async def _process_request(self, method, default_status=200):
        if not method:
            raise web.HTTPMethodNotAllowed

        response = {
            'result': None,
            'success': False
        }
        status = default_status
        try:
            await method.from_http(self.request)
            response = await method.get_output()
        except (
                ObjectNotFoundException,
                ObjectAlreadyExistException
        ) as exc:
            response['errors'] = method.errors
            response['errors'].append(exc.to_dict())
            status = exc.status_code

        except BadRequestException as exc:
            response['errors'] = method.errors
            response['errors'].append(exc.to_dict())
            status = exc.status_code

        except Exception as exc:
            response['errors'] = method.errors
            response['errors'].append({
                'code': 500,
                'message': str(exc)
            })
            status = 500
        if response.get('errors') and status == default_status:
            error = response.get('errors', [{}])[0]
            status = 500 if isinstance(error, str) else error.get('code', default_status)

        self._response = response
        return web.json_response(response, status=status)

    async def get(self):
        return await self._process_request(self.get_method)

    async def post(self):
        resp = self._set_location_to_response(await self._process_request(self.post_method, default_status=201))
        return resp

    async def put(self):
        resp = self._set_location_to_response(await self._process_request(self.put_method))
        return resp

    async def delete(self):
        return await self._process_request(self.delete_method, default_status=204)
