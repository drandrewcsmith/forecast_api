import numpy as np


from forecast_api.lib.exceptions import (
    InvalidAverageWindowParameter,
)

from forecast_api.lib.param_parsers import (
    parse_integer_param,
)


def parse_params(**params):

    if 'window' not in params:
        raise InvalidAverageWindowParameter(f"'window' is a natural number and is a required parameter")
    window = parse_integer_param('window', params['window'], param_min=1)

    return {
        'window': window,
    }


def model(input_array, horizon, window):
    return [input_array[-window:].mean()]*horizon


class Average:

    def __init__(self, params_parser, forecast_method):
        self._parse_params = params_parser
        self._forecast_method = forecast_method

    def fit_forecast(self, input_data, forecast_horizon, **params):
        return self.forecast(input_data, forecast_horizon, **params)

    def forecast(self, input_data, forecast_horizon, **params):
        params = self._parse_params(**params)

        forecast = self._forecast_method(
            np.array(input_data),
            forecast_horizon,
            params.get('window')
        )

        return {
            'forecast': forecast,
            'params': params
        }


if __name__ == '__main__':

    test_data = [
        0, 1, 2, 3, 4, 5, 4, 3, 2, 1,
        0, 1, 2, 3, 4, 5, 4, 3, 2, 1,
        0, 1, 2, 3, 4, 5, 4, 3, 2, 1,
        0, 1, 2, 3, 4, 5, 4, 3, 2, 1,
        0, 1, 2, 3, 4, 5, 4, 3, 2, 1,
    ]

    test_forecast_horizon = 12
    test_params = {
        'window': 3,
    }
    average = Average(
        parse_params,
        model
    )
    res = average.fit_forecast(
        test_data,
        test_forecast_horizon,
        **test_params
    )
    print('#'*50)
    print(res['forecast'])
    for key in sorted(res['params']):
        value = res['params'][key]
        print(f'{key} = {value}')

    fitted_params = res['params']
    res = average.forecast(
        test_data,
        test_forecast_horizon,
        **fitted_params
    )
    print('#'*50)
    print(res['forecast'])
    for key in sorted(res['params']):
        value = res['params'][key]
        print(f'{key} = {value}')
