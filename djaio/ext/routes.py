# -*- coding: utf-8 -*-
import inspect


def _get_linepath(item):
    _filename = inspect.getfile(item)
    _source = open(_filename).readlines()
    lineno = _source.index(inspect.getsourcelines(item)[0][0]) + 1
    return '{}:{}'.format(_filename, lineno)

def print_routes(app):
    maxLenName = 0
    maxLenPath = 0
    maxLenClassName = 0

    _urlconf = {}
    for name, resource in app.router.named_resources().items():
        _urlconf[name] = {
            'routes': {}
        }

        for route in resource._routes:
            path = getattr(resource, '_path', getattr(resource, '_formatter', ''))
            module_path = "%s.%s" % (route.handler.__module__, route.handler.__name__)

            _urlconf[name]['path'] = path

            _urlconf[name]['routes'][route.method] = {
                'module_path': module_path,
                'line_path': _get_linepath(route.handler)
            }

            maxLenPath = max(maxLenPath, len(path))
            maxLenClassName = max(maxLenClassName, len(module_path))
        maxLenName = max(maxLenName, len(name))


    for name, route in _urlconf.items():
        print('-' * 13)
        print(name.ljust(maxLenName + 2), route['path'])
        for method, path in route['routes'].items():
            _repstr = ' - {} {} {}'.format(
                method.ljust(10),
                path['module_path'].ljust(maxLenClassName + 2),
                path['line_path'],
            )
            print(_repstr)

