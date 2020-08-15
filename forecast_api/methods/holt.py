import numpy as np


from forecast_api.lib.exceptions import (
    InvalidTrendParameters
)
from forecast_api.lib.param_parsers import (
    parse_boolean_param,
    parse_numeric_param,
)


def parse_params(**params):

    alpha = None
    if 'alpha' in params and params['alpha'] is not None:
        alpha = parse_numeric_param('alpha', params['alpha'], param_min=0, param_max=1)

    beta = None
    if 'beta' in params and params['beta'] is not None:
        beta = parse_numeric_param('beta', params['beta'], param_min=0, param_max=1)

    phi = None
    if 'phi' in params and params['phi'] is not None:
        phi = parse_numeric_param('phi', params['phi'], param_min=0, param_max=1)

    initial_level = None
    if 'initial_level' in params and params['initial_level'] is not None:
        initial_level = parse_numeric_param('initial_level', params['initial_level'], param_min=0)

    initial_slope = None
    if 'initial_slope' in params and params['initial_slope'] is not None:
        initial_slope = parse_numeric_param('initial_slope', params['initial_slope'])

    exponential = False
    if 'exponential' in params and params['exponential'] is not None:
        exponential = parse_boolean_param('exponential', params['exponential'])

    damped = False
    if 'damped' in params and params['damped'] is not None:
        damped = parse_boolean_param('damped', params['damped'])

    if exponential and initial_level == 0.0:
        raise InvalidTrendParameters(f'initial level can not be {initial_level} if exponential={exponential}')
    if damped and not exponential:
        raise InvalidTrendParameters(f'exponential must True if damped = {damped}')
    if phi is not None and not damped:
        raise InvalidTrendParameters(f'damped must be True if phi = {phi}')

    optimized_alpha = True if alpha is None else False
    optimized_initial_level = True if initial_level is None else False
    optimized_beta = True if beta is None else False
    optimized_initial_slope = True if initial_slope is None else False
    optimized_phi = True if (phi is None and damped is True) else False

    to_fit = False
    if optimized_alpha or optimized_initial_level or optimized_beta or \
            optimized_initial_slope or optimized_phi:
        to_fit = True

    return {
        'alpha': alpha,
        'initial_level': initial_level,
        'beta': beta,
        'initial_slope': initial_slope,
        'phi': phi,
        'exponential': exponential,
        'damped': damped,
        'to_fit': to_fit,
        'optimized_alpha': optimized_alpha,
        'optimized_initial_level': optimized_initial_level,
        'optimized_beta': optimized_beta,
        'optimized_initial_slope': optimized_initial_slope,
        'optimized_phi': optimized_phi,
    }


class Holt:

    def __init__(self, params_parser, forecast_method):
        self._parse_params = params_parser
        self._forecast_method = forecast_method

    def fit_forecast(self, input_data, forecast_horizon, **params):
        params = self._parse_params(**params)

        model = self._forecast_method(
            np.array(input_data),
            exponential=params.get('exponential', None),
            damped=params.get('damped', None)
        )
        fit = model.fit(
            smoothing_level=params.get('alpha', None),
            initial_level=params.get('initial_level', None),
            smoothing_slope=params.get('beta', None),
            initial_slope=params.get('initial_slope', None),
            damping_slope=params.get('phi', None),
            optimized=params.get('to_fit', True)
        )
        params['alpha'] = fit.params['smoothing_level']
        params['initial_level'] = fit.params['initial_level']
        params['beta'] = fit.params['smoothing_slope']
        params['initial_slope'] = fit.params['initial_slope']
        params['phi'] = fit.params['damping_slope']

        forecast = fit.forecast(
            forecast_horizon
        )
        return {
            'forecast': list(forecast),
            'params': params
        }

    def forecast(self, input_data, forecast_horizon, **params):
        params = self._parse_params(**params)
        if params['to_fit']:
            raise ValueError(f'use fit_forecast to fit model with provided parameters')
        model = self._forecast_method(
            np.array(input_data),
            np.array(input_data),
            exponential=params.get('exponential', None),
            damped=params.get('damped', None)
        )
        forecast = model.predict(
            {
                'smoothing_level': params.get('alpha', None),
                'initial_level': params.get('initial_level', None),
                'smoothing_slope': params.get('beta', None),
                'initial_slope': params.get('initial_slope', None),
                'damping_slope': params.get('phi', None),
            },
            start=len(input_data),
            end=len(input_data)+forecast_horizon-1
        )
        return {
            'forecast': list(forecast),
            'params': params
        }

if __name__ == '__main__':

    from statsmodels.tsa.api import Holt as smholt

    test_data = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8]
    test_forecast_horizon = 12
    test_params = {
        # 'alpha': 0.0,
        # 'initial_level': 50,
        # 'beta': 0.02,
        # 'initial_slope': 0.0,
        # 'exponential': True,
        # 'damped': True,
        # 'phi': 0.1
    }
    hes = Holt(
        parse_params,
        smholt
    )
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

    fitted_params = res['params']
    res = hes.forecast(
        test_data,
        test_forecast_horizon,
        **fitted_params
    )
    print('#'*50)
    print(res['forecast'])
    for key in sorted(res['params']):
        value = res['params'][key]
        print(f'{key} = {value}')
