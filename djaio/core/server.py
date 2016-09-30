import os
import importlib
from aiohttp import web
import djaio.core.settings as _settings
from djaio.core import urlconf


def get_settings():
    settings_module = os.environ.get('SETTINGS', 'app.settings')
    settings = None
    try:
        settings = importlib.import_module(settings_module)
    except ImportError:
        print('Settings module not found. Using the default one.')

    if settings:
        for k, v in settings.__dict__.items():
            setattr(_settings, k, v)
    return _settings


def discover_urls(app):
    settings = getattr(app, 'settings', None)
    if settings is None:
        return
    for _app in settings.INSTALLED_APPS:
        importlib.import_module('{}.urls'.format(_app))
    urlconf.setup(app)


def get_middlewares(settings):
    middleware_list = getattr(settings, 'MIDDLEWARES', [])
    out = []
    for item in middleware_list:
        module_name, factory = item.rsplit('.', 1)
        module = importlib.import_module(module_name)
        try:
            out.append(getattr(module, factory))
        except KeyError:
            continue
    return out

def get_router(settings):
    custom_router = getattr(settings, 'CUSTOM_ROUTER', None)
    if custom_router:
        module_name, factory = custom_router.rsplit('.', 1)
        module = importlib.import_module(module_name)
        try:
            return (getattr(module, factory))
        except KeyError:
            pass


def init_app():
    settings = get_settings()
    middlewares = get_middlewares(settings)
    router = get_router(settings)
    app = web.Application(middlewares=middlewares, debug=settings.DEBUG, router=router() if router else None)
    app.settings = settings
    discover_urls(app)
    return app
