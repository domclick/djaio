import asyncio
import aiohttp
from aiohttp import web
from aiohttp.hdrs import METH_ALL
import aiohttp_jinja2

from djaio.core.exceptions import ObjectNotFoundException, ObjectAlreadyExistException
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
            await self.get_context_data()
        )

    async def get(self):
        body = await self.render()
        return body


class JsonView(web.View):
    get_method = None
    post_method = None
    put_method = None
    delete_method = None

    empty_response = {
        'result': None,
        'success': False
    }

    async def _process_request(self, method, default_status=200):
        if not method:
            raise web.HTTPMethodNotAllowed
        await method.from_http(self.request)
        response = self.empty_response
        status = default_status
        try:
            response = await method.get_output()
        except (
                ObjectNotFoundException,
                ObjectAlreadyExistException
        ) as exc:
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
        return web.json_response(response, status=status)

    async def get(self):
        return await self._process_request(self.get_method)

    async def post(self):
        return await self._process_request(self.post_method, default_status=201)

    async def put(self):
        return await self._process_request(self.put_method)

    async def delete(self):
        return await self._process_request(self.delete_method, default_status=204)
