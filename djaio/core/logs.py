# -*- coding: utf-8 -*-

import logging.config

_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s][logger:%(name)s][MODULE:"%(module)s"][process:%(process)d][thread:%(thread)d] - "%(message)s"'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level':'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local5',
            'address': '/dev/log',
            'formatter': 'verbose'
       },
    },
    'loggers': {
        'djaio_logger': {
            'handlers': ['console', 'syslog'],
            'level': 'DEBUG',
        },
    },
}


def setup(app):
    logger_config = getattr(app.settings, 'LOGGING', {})
    _LOGGING.update(**logger_config)
    logging.config.dictConfig(_LOGGING)