import sys
import asyncio
from aiohttp import web
from djaio.core.server import init_app


class Djaio(object):

    def __init__(self, custom_init=None, loop=None):
        self.argv = sys.argv
        self.app = init_app(loop=loop)
        if callable(custom_init):
            custom_init(self.app)

    def run(self):
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'
        if subcommand == 'runserver':
            try:
                host, port = self.argv[2].split(':')
                if not port:
                    port = '8080'
            except (IndexError, ValueError):
                print('WARNING! Incorrect host:port - using default settings.')
                host = '0.0.0.0'
                port = '8080'
            web.run_app(self.app, host=host, port=port)

        elif subcommand == 'help':
            print('=' * 60)
            print('Usage: {} <command> <options>'.format(self.argv[0].rsplit('/', 1)[1]))
            print('Available commands:')
            print(' * help - shows this message')
            print(' * runserver host:port - runs web server')
            for key, comm_obj in self.app.commands.items():
                print(' * {} <options> - {}'.format(key, comm_obj.get('description')))
            print('=' * 60)

        elif subcommand in self.app.commands:
            _args = self.argv[2:]
            _coro = self.app.commands[subcommand].get('func')
            self.app.loop.run_until_complete(_coro(self.app, *_args))