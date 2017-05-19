#!-*- coding: utf-8 -*-
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


def _import_func(dotted_str):
    """
    Imports function using dot-notation string.
    :param dotted_str: Dotted path to function like `module.submodule.func`
    :return: func
    """
    module_name, factory = dotted_str.rsplit('.', 1)
    module = importlib.import_module(module_name)
    try:
        return getattr(module, factory)
    except KeyError:
        raise ImportError('There is no {} in {} module!'.format(factory, module))


def get_middlewares(settings):
    middleware_list = getattr(settings, 'MIDDLEWARES', [])
    out = []
    for item in middleware_list:
        try:
            out.append(_import_func(item))
        except ImportError:
            continue
    return out


def get_commands(settings):
    commands = getattr(settings, 'MANAGEMENT_COMMANDS', [])
    out = {}
    for item in commands:
        try:
            _func = _import_func(item)
        except ImportError:
            continue
        if hasattr(_func, 'command_name'):
            _name = _func.command_name
        else:
            _name = _func.__name__
        out[_name] = {
            'func': _func,
            'description': getattr(_func, 'command_description', '')
        }
    return out


def get_router(settings):
    custom_router = getattr(settings, 'CUSTOM_ROUTER', None)
    if custom_router:
        return _import_func(custom_router)


def init_app(loop=None):
    settings = get_settings()
    middlewares = get_middlewares(settings)
    router = get_router(settings)
    app = web.Application(
        middlewares=middlewares,
        debug=settings.DEBUG,
        router=router() if router else None
    )
    app._set_loop(loop)
    app.settings = settings
    discover_urls(app)
    app.commands = get_commands(settings)
    return app
