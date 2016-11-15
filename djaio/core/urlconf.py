#!-*- coding: utf-8 -*-
from collections import namedtuple


urls = []
_url_type = namedtuple('url_item', ['method', 'path', 'handler', 'name'])


def url(method, path, handler, name=None):
    urls.append(_url_type(method=method, path=path, handler=handler, name=name))


def setup(app):
    app.urls = {}
    for url in urls:
        app.urls[url.handler.__name__] = url.name
        app.router.add_route(url.method, url.path, url.handler, name=url.name)


