#!-*- coding: utf-8 -*-
import inspect
from collections import namedtuple
from aiohttp.web import UrlDispatcher
from aiohttp import hdrs
from aiohttp.test_utils import make_mocked_request

VERBS = [
    hdrs.METH_GET.lower(),
    hdrs.METH_POST.lower(),
    hdrs.METH_PUT.lower(),
    hdrs.METH_DELETE.lower()
]


class DjaioUrlDispatcher(UrlDispatcher):
    def add_route(self, methods, path, handler, *, name=None, expect_handler=None):
        """
        Replace a base add_route to own for ClassBasedViews.
        """
        resource = self.add_resource(path, name=name)
        if isinstance(methods, str):
            methods = [methods]
        for m in methods:
            resource.add_route(m, handler, expect_handler=expect_handler)


urls = []
_url_type = namedtuple('url_item', ['method', 'path', 'handler', 'name'])


def url(method, path, handler, name=None):
    urls.append(_url_type(method=method, path=path, handler=handler, name=name))


class handle_url:  # noqa
    def __init__(self, path, name=None):
        self.path = path
        self.name = name

    def get_name(self, cls):
        if not self.name:
            return cls.__name__
        return self.name

    def __call__(self, cls):
        if inspect.isclass(cls):
            http_meths = []
            _view = cls(make_mocked_request(hdrs.METH_GET, '/'))
            for verb in VERBS:
                if getattr(_view, '{}_method'.format(verb)):
                    http_meths.append(verb)
            url(method=http_meths, path=self.path, handler=cls, name=self.get_name(cls))
        return cls


def setup(app):
    app.urls = {}
    for url in urls:
        app.urls[url.handler.__name__] = url.name
        app.router.add_route(url.method, url.path, url.handler, name=url.name)
