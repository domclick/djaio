import logging
import os
from typing import Dict

from aiohttp.web import Request
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from raven_aiohttp import AioHttpTransport


class DjaioSentryHandler(SentryHandler):
    def _emit(self, record, **kwargs):
        request = getattr(record, 'request', None)
        if request is None or not isinstance(request, Request):
            return super()._emit(record, **kwargs)

        record.request = self._create_request_data(request)
        return super()._emit(record, **kwargs)

    @staticmethod
    def _create_request_data(request: Request) -> Dict:
        return {
            'url': str(request.url),
            'query_string': request.query_string,
            'method': request.method,
            'headers': dict(request.headers),
        }


def setup(app):
    version = getattr(app.settings, 'VERSION', 1)
    environment = getattr(app.settings, 'ROLE', None) or os.environ.get('ROLE')
    dsn = getattr(app.settings, 'SENTRY_DSN', None)
    tags = getattr(app.settings, 'SENTRY_TAGS', None)

    client = Client(dsn=dsn, transport=AioHttpTransport,
                    version=version, environment=environment,
                    tags=tags)

    handler = DjaioSentryHandler(client=client)
    handler.setLevel(logging.ERROR)
    setup_logging(handler)

    app.raven = client
