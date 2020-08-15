import numpy as np

from forecast_api.lib.exceptions import (
    InvalidSeasonalParameters,
    InvalidTrendParameters
)
from forecast_api.lib.param_parsers import (
    parse_boolean_param,
    parse_integer_param,
    parse_numeric_param,
    parse_string_param,
)


def parse_params(**params):

    alpha = None
    if 'alpha' in params and params['alpha'] is not None:
        alpha = parse_numeric_param('alpha', params['alpha'], param_min=0, param_max=1)

    beta = None
    if 'beta' in params and params['beta'] is not None:
        beta = parse_numeric_param('beta', params['beta'], param_min=0, param_max=1)

    gamma = None
    if 'gamma' in params and params['gamma'] is not None:
        gamma = parse_numeric_param('gamma', params['gamma'], param_min=0, param_max=1)

    phi = None
    if 'phi' in params and params['phi'] is not None:
        phi = parse_numeric_param('phi', params['phi'], param_min=0, param_max=1)

    initial_level = None
    if 'initial_level' in params and params['initial_level'] is not None:
        initial_level = parse_numeric_param('initial_level', params['initial_level'], param_min=0)

    initial_slope = None
    if 'initial_slope' in params and params['initial_slope'] is not None:
        initial_slope = parse_numeric_param('initial_slope', params['initial_slope'])

    trend = None
    if 'trend' in params and params['trend'] is not None:
        trend = parse_string_param('trend', params['trend'], ['add', 'mul'])

    damped = False
    if 'damped' in params and params['damped'] is not None:
        damped = parse_boolean_param('damped', params['damped'])

    seasonal = None
    if 'seasonal' in params and params['seasonal'] is not None:
        seasonal = parse_string_param('seasonal', params['seasonal'], ['add', 'mul'])

    seasonal_periods = None
    if 'seasonal_periods' in params and params['seasonal_periods'] is not None:
        seasonal_periods = parse_integer_param('seasonal_periods', params['seasonal_periods'], param_min=1)

    if trend == 'mul' and initial_level == 0.0:
        raise InvalidTrendParameters(f'initial level can not be {initial_level} if trend={trend}')
    if damped and not trend:
        raise InvalidTrendParameters(f'trend must be provided if damped = {damped}')
    if phi is not None and not damped:
        raise InvalidTrendParameters(f'damped must be True if phi = {phi}')

    if seasonal and seasonal_periods is None:
        raise InvalidSeasonalParameters(f'seasonal_periods must be provided if seasonal = {seasonal}')
    if seasonal_periods is not None and seasonal is None:
        raise InvalidSeasonalParameters(f'seasonal must be provided if seasonal_periods = {seasonal_periods}')
    if gamma is not None and seasonal is None:
        raise InvalidSeasonalParameters(f'seasonal and seasonal_periods must be provided if gamma = {gamma}')

    optimized_alpha = True if alpha is None else False
    optimized_initial_level = True if initial_level is None else False
    optimized_beta = True if beta is None else False
    optimized_initial_slope = True if initial_slope is None else False
    optimized_phi = True if (phi is None and damped is True) else False
    optimized_seasonal = True if seasonal else False
    optimized_gamma = True if (optimized_seasonal and gamma is None) else False

    to_fit = False
    if optimized_alpha or optimized_initial_level or optimized_beta or \
            optimized_initial_slope or optimized_seasonal or optimized_gamma or optimized_phi:
        to_fit = True

    params = {
        'alpha': alpha,
        'initial_level': initial_level,
        'beta': beta,
        'initial_slope': initial_slope,
        'trend': trend,
        'damped': damped,
        'phi': phi,
        'seasonal': seasonal,
        'seasonal_periods': seasonal_periods,
        'gamma': gamma,
        'optimized_alpha': optimized_alpha,
        'optimized_initial_level': optimized_initial_level,
        'optimized_beta': optimized_beta,
        'optimized_initial_slope': optimized_initial_slope,
        'optimized_phi': optimized_phi,
        'optimized_seasonal': optimized_seasonal,
        'optimized_gamma': optimized_gamma,
        'to_fit': to_fit,
    }
    return params


class HoltWinter:

    def __init__(self, params_parser, forecast_method):
        self._parse_params = params_parser
        self._forecast_method = forecast_method

    def _parse_data(self, input_data):
        try:
            input_data = input_data.values
            input_data_length = input_data.shape[0]
        except AttributeError:
            input_data = np.array(input_data)
            input_data_length = len(input_data)
        return input_data, input_data_length

    def _create_model(self, input_data, params):
        return self._forecast_method(
            input_data,
            trend=params.get('trend', None),
            damped=params.get('damped', None),
            seasonal=params.get('seasonal', None),
            seasonal_periods=params.get('seasonal_periods', None)
        )

    def _fit_model(self, model, params):
        return model.fit(
            smoothing_level=params.get('alpha', None),
            smoothing_slope=params.get('beta', None),
            smoothing_seasonal=params.get('gamma', None),
            damping_slope=params.get('phi', None),
            optimized=params.get('to_fit', True),
            initial_level=params.get('initial_level', None),
            initial_slope=params.get('initial_slope', None),
        )

    def _fit_params(self, fit, params):
        def _parse_np_nan(value):
            if isinstance(value, np.float):
                return None if np.isnan(value) else float(value)
            return None
        params['alpha'] = _parse_np_nan(fit.params['smoothing_level'])
        params['initial_level'] = _parse_np_nan(fit.params['initial_level'])
        params['beta'] = _parse_np_nan(fit.params['smoothing_slope'])
        params['initial_slope'] = _parse_np_nan(fit.params['initial_slope'])
        params['phi'] = _parse_np_nan(fit.params['damping_slope'])
        params['initial_seasons'] = list(fit.params['initial_seasons'])
        params['gamma'] = _parse_np_nan(fit.params['smoothing_seasonal'])
        return params

    def _forecast(self, fit, forecast_horizon):
        return fit.forecast(
            forecast_horizon
        )

    def _predict(self, model, start_index, end_index, params):
        return model.predict(
            {
                'smoothing_level': params.get('alpha', None),
                'smoothing_slope': params.get('beta', None),
                'smoothing_seasonal': params.get('gamma', None),
                'damping_slope': params.get('phi', None),
                'initial_level': params.get('initial_level', None),
                'initial_slope': params.get('initial_slope', None),
            },
            start=start_index,
            end=end_index
        )

    def forecast(self, input_data, forecast_horizon, **params):
        params = self._parse_params(**params)
        if params['to_fit']:
            raise ValueError(f'use fit_forecast to fit model with provided parameters')
        input_data, input_data_length = self._parse_data(input_data)
        model = self._create_model(input_data, params)
        forecast = self._predict(model, input_data_length, input_data_length+forecast_horizon-1, params)
        return {
            'forecast': forecast,
            'params': params
        }

    def fit_forecast(self, input_data, forecast_horizon, **params):
        params = self._parse_params(**params)
        input_data, input_data_length = self._parse_data(input_data)
        model = self._create_model(input_data, params)
        fit = self._fit_model(model, params)
        fit_params = self._fit_params(fit, params)
        forecast = self._forecast(fit, forecast_horizon)

        return {
            'forecast': list(forecast),
            'params': fit_params
        }


if __name__ == '__main__':

    from statsmodels.tsa.api import ExponentialSmoothing as smholtwinter
    test_data = [
        1.1, 1.9, 3.1, 3.9, 5.1, 3.9, 3.1, 1.9, 1.1, 2.1, 2.9, 4.1, 4.9, 4.1, 2.9, 2.1, 1, 2, 3, 4, 5, 4, 3, 2, 1
    ]

    test_forecast_horizon = 12
    test_params = {
        #'alpha': 0.5,
        #'initial_level': 1.0,
        #'beta': 0.02,
        #'initial_slope': 0.0,
        'trend': 'add',
        #'damped': True,
        #'phi': 0.1,
        'seasonal': 'add',
        'seasonal_periods': 8,
        #'gamma': 0.01,
    }

    hes = HoltWinter(parse_params, smholtwinter)
    res = hes.fit_forecast(
        test_data,
        test_forecast_horizon,
        **test_params
    )
    print('#'*50)
    print(res['forecast'])
    for key in sorted(res['params']):
        value = res['params'][key]
        print(f'{key} = {value}')

    print('#'*50)
    res = hes.forecast(
        test_data,
        test_forecast_horizon,
        **test_params
    )
    print(res)
