# -*- coding:utf-8 -*-
import logging
import sys
from logging.config import dictConfig

from scrapy_aio.conf.settings import Settings
from types import MethodType
from scrapy_aio.log_handler import LogHandler
# logger = logging.getLogger(__name__)
logger = LogHandler(__name__)


class TopLevelFormatter(logging.Filter):
    """Keep only top level loggers's name (direct children from root) from
    records.

    This filter will replace Scrapy loggers' names with 'scrapy'. This mimics
    the old Scrapy log behaviour and helps shortening long names.

    Since it can't be set for just one logger (it won't propagate for its
    children), it's going to be set in the root handler, with a parametrized
    ``loggers`` list where it should act.
    """

    def __init__(self, loggers=None):
        self.loggers = loggers or []

    def filter(self, record):
        if any(record.name.startswith(l + '.') for l in self.loggers):
            record.name = record.name.split('.', 1)[0]
        return True


DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'scrapy': {
            'level': 'DEBUG',
        },
        'twisted': {
            'level': 'ERROR',
        },
    }
}


def configure_logging(settings=None, install_root_handler=True):
    if not sys.warnoptions:
        # Route warnings through python logging
        logging.captureWarnings(True)

    dictConfig(DEFAULT_LOGGING)

    if isinstance(settings, dict) or settings is None:
        settings = Settings(settings)
    if settings.getbool('LOG_STDOUT'):
        pass
    if install_root_handler:
        LogHandler.__new__(LogHandler, level='ERROR')


def logformatter_adapter(logkws):
    """
    Helper that takes the dictionary output from the methods in LogFormatter
    and adapts it into a tuple of positional arguments for logger.log calls,
    handling backward compatibility as well.
    """

    level = logkws.get('level', logging.INFO)
    message = logkws.get('format', logkws.get('msg'))
    # NOTE: This also handles 'args' being an empty dict, that case doesn't
    # play well in logger.log calls
    args = logkws if not logkws.get('args') else logkws['args']

    return (level, message, args)
