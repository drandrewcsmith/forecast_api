import falcon
import logging

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

        except Exception:
            _log.exception('Problem generating forecast')
            response.status = falcon.HTTP_INTERNAL_SERVER_ERROR
