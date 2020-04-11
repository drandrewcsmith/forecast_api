import falcon
import logging

from forecast_api.methods.exceptions import InvalidParameter

_log = logging.getLogger(__name__)


class ForecastResource(object):
    def __init__(self, method):
        self._method = method

    def on_post(self, request, response):

        try:
            response.status = falcon.HTTP_OK

            input_data = request.media['input_data']
            forecast_horizon = request.media['forecast_horizon']
            params = request.media['params']

            forecast = self._method.fit_forecast(
                input_data,
                forecast_horizon,
                **params
            )
            response.media = forecast
        except InvalidParameter as e:
            _log.exception('Improperly specified parameter')
            raise falcon.HTTPBadRequest(description=f'Bad parameter: {e}')
        except ValueError as e:
            _log.exception('Improperly specified parameter')
            raise falcon.HTTPBadRequest(description=f'Bad parameter: {e}')
        except Exception as e:
            _log.exception('Problem generating forecast')
            raise falcon.HTTPInternalServerError(description=f'{e}')
