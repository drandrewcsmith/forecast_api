import traceback
import falcon
import structlog

from forecast_api.api.ping import PingResource
from forecast_api.api.forecast import ForecastResource
from forecast_api.api.forecast import GenericForecastResource

from forecast_api.app import create_container

_log = structlog.get_logger(__name__)


def configure_callable(ini_path=None):
    return create_callable(create_container(ini_path))


def handle_uncaught_exceptions(ex, request, response, params):
    if isinstance(ex, falcon.HTTPError):
        raise ex

    _log.error(f'unexpected {ex!r}:\n{traceback.format_tb(ex.__traceback__)}')

    raise falcon.HTTPInternalServerError(
        description='I am sorry Dave, I am afraid, I cannot do that'
    )


def create_callable(container):
    app = falcon.API()
    app.add_route(
        '/alert/ping',
        PingResource()
    )
    app.add_route(
        '/v1/forecast/holt',
        ForecastResource(
            container('services.methods.holt')
        )
    )
    app.add_route(
        '/v1/forecast/holtwinter',
        ForecastResource(
            container('services.methods.holtwinter')
        )
    )
    app.add_route(
        '/v1/forecast/{forecast_method}',
        GenericForecastResource(
        )
    )

    app.add_error_handler(Exception, handle_uncaught_exceptions)
    return app
