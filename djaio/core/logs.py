# -*- coding: utf-8 -*-
import sys
import logging.config
from djaio.core.utils import deep_merge


class ColoredFormatter(logging.Formatter):
    RESET = '\x1B[0m'
    RED = '\x1B[31m'
    YELLOW = '\x1B[33m'
    BRGREEN = '\x1B[01;32m'  # grey in solarized for terminals

    def format(self, record, color=False):
        message = super().format(record)

        if not color:
            return message

        level_no = record.levelno
        if level_no >= logging.CRITICAL:
            color = self.RED
        elif level_no >= logging.ERROR:
            color = self.RED
        elif level_no >= logging.WARNING:
            color = self.YELLOW
        elif level_no >= logging.INFO:
            color = self.RESET
        elif level_no >= logging.DEBUG:
            color = self.BRGREEN
        else:
            color = self.RESET
        message = color + message + self.RESET
        return message


class ColoredHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stdout):
        super().__init__(stream)

    def format(self, record, colour=False):
        if not isinstance(self.formatter, ColoredFormatter):
            self.formatter = ColoredFormatter('[%(asctime)s] [%(levelname)s][MODULE:"%(module)s"] - "%(message)s"')

        return self.formatter.format(record, colour)

    def emit(self, record):
        stream = self.stream
        try:
            msg = self.format(record, stream.isatty())
            stream.write(msg)
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s][MODULE:"%(module)s"] - "%(message)s"'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'djaio_logger': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


def setup(app):
    logger_config = getattr(app.settings, 'LOGGING', {})
    _LOGGING = deep_merge(LOGGING, logger_config)
    if app.settings.DEBUG:
        _LOGGING['handlers']['console']['class'] = 'djaio.core.logs.ColoredHandler'
    logging.config.dictConfig(_LOGGING)
