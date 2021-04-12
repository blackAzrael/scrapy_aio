# -*- coding:utf-8 -*-
import logging
import sys
from logging.config import dictConfig

from scrapy_aio.conf.settings import Settings

logger = logging.getLogger(__name__)


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
        sys.stdout = StreamLogger(logging.getLogger('stdout'))
    if install_root_handler:
        install_mavic_root_handler(settings)


def install_mavic_root_handler(settings):
    global _mavic_root_handler

    if (_mavic_root_handler is not None
            and _mavic_root_handler in logging.root.handlers):
        logging.root.removeHandler(_mavic_root_handler)
    logging.root.setLevel(logging.NOTSET)
    _mavic_root_handler = _get_handler(settings)
    logging.root.addHandler(_mavic_root_handler)



def get_mavic_root_handler():
    return _mavic_root_handler


_mavic_root_handler = None


def _get_handler(settings):
    """ Return a log handler object according to settings """
    filename = settings.get('LOG_FILE')
    if filename:
        encoding = settings.get('LOG_ENCODING')
        handler = logging.FileHandler(filename, encoding=encoding)
    elif settings.getbool('LOG_ENABLED'):
        handler = logging.StreamHandler()
    else:
        handler = logging.NullHandler()

    formatter = logging.Formatter(
        fmt=settings.get('LOG_FORMAT'),
        datefmt=settings.get('LOG_DATEFORMAT')
    )

    handler.setFormatter(formatter)
    handler.setLevel(settings.get('LOG_LEVEL'))
    if settings.getbool('LOG_SHORT_NAMES'):
        handler.addFilter(TopLevelFormatter(['scrapy_aio']))
    return handler


class StreamLogger(object):

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        for h in self.logger.handlers:
            h.flush()


class LogCounterHandler(logging.Handler):

    def __init__(self, crawler, *args, **kwargs):
        super(LogCounterHandler, self).__init__(*args, **kwargs)
        self.crawler = crawler

    def emit(self, record):
        sname = 'log_count/{}'.format(record.levelname)
        self.crawler.stats.inc_value(sname)


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
