import os
from configparser import ConfigParser
from functools import partial

import structlog
from knot import Container

from forecast_api.methods import Holt
from forecast_api.methods import parse_holt_params
from forecast_api.methods import HoltWinter
from forecast_api.methods import parse_holtwinter_params


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
        partial(_forecast_method_holt),
        name='services.methods.holt',
    )
    container.add_service(
        partial(
            _forecast_params_holt
        ),
        name='services.methods.parse_holt_params'
    )
    container.add_service(
        partial(
            _forecast_method_holtwinter
        ),
        name='services.methods.holtwinter',
    )
    container.add_service(
        partial(
            _forecast_params_holtwinter
        ),
        name='services.methods.parse_holtwinter_params'
    )

    return container


def _forecast_params_holt(c):
    return partial(parse_holt_params)


def _forecast_method_holt(c):
    return Holt(
        c('services.methods.parse_holt_params')
    )


def _forecast_params_holtwinter(c):
    return partial(parse_holtwinter_params)


def _forecast_method_holtwinter(c):
    return HoltWinter(
        c('services.methods.parse_holtwinter_params')
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
