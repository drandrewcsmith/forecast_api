import os
import structlog

from configparser import ConfigParser
from functools import partial
from knot import Container

from statsmodels.tsa.api import ExponentialSmoothing as smholtwinter
from statsmodels.tsa.api import Holt as smholt

from forecast_api.methods import Holt
from forecast_api.methods import holt_parse_params
from forecast_api.methods import HoltWinter
from forecast_api.methods import holtwinter_parse_params


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
        partial(_forecast_holt_method),
        name='services.methods.holt',
    )
    container.add_service(
        partial(_forecast_holt_model),
        name='services.methods.holt_model',
    )
    container.add_service(
        partial(_forecast_holt_params),
        name='services.methods.holt_parse_params'
    )

    container.add_service(
        partial(_forecast_holtwinter_method),
        name='services.methods.holtwinter',
    )
    container.add_service(
        partial(_forecast_holtwinter_model),
        name='services.methods.holtwinter_model'
    )
    container.add_service(
        partial(_forecast_holtwinter_params),
        name='services.methods.holtwinter_parse_params'
    )

    return container


def _forecast_holt_params(c):
    return partial(holt_parse_params)


def _forecast_holt_model(c):
    return partial(smholt)


def _forecast_holt_method(c):
    return Holt(
        c('services.methods.holt_parse_params'),
        c('services.methods.holt_model')
    )


def _forecast_holtwinter_params(c):
    return partial(holtwinter_parse_params)


def _forecast_holtwinter_model(c):
    return partial(smholtwinter)


def _forecast_holtwinter_method(c):
    return HoltWinter(
        c('services.methods.holtwinter_parse_params'),
        c('services.methods.holtwinter_model')
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
