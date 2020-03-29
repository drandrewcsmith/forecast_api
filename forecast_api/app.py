import os
from configparser import ConfigParser
from functools import partial

import structlog
from knot import Container

from forecast_api.methods import Holt


def create_container(ini_path=None) -> Container:
    ini_path = ini_path or os.environ['FORECAST_API_CONFIG']
    _setup_logging(ini_path)
    container = Container({'ini_path': ini_path})
    container.add_provider(
        name='config',
        provider=_read_config,
        cache=True,
    )
    container.add_service(
        partial(_holt_forecast_method),
        name='services.methods.holtes',
    )
    return container


def _holt_forecast_method(c):
    return Holt(
    )


def _read_config(c) -> ConfigParser:
    config = ConfigParser()
    assert config.read(c.get('ini_path')), 'Cannot read config file'
    return config


def _setup_logging(config_path):
    import logging.config

    logging.config.fileConfig(config_path)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
