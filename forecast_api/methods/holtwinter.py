import numbers
import numpy as np

from statsmodels.tsa.api import ExponentialSmoothing as smholtwinter
from forecast_api.methods.exceptions import InvalidParameter


def parse_params(**params):

    def parse_numeric_param(param_name, param_value, param_min=None, param_max=None):
        if not isinstance(param_value, (int, float)) or isinstance(param_value, bool):
            raise InvalidParameter(f'{param_name} ({param_value}) should be a real number')
        if param_min is not None and param_value < param_min:
            raise InvalidParameter(f'{param_name} ({param_value}) should be >= {param_min}')
        if param_max is not None and param_value > param_max:
            raise InvalidParameter(f'{param_name} ({param_value}) should be <= {param_max}')
        return float(param_value)

    def parse_integer_param(param_name, param_value, param_min=None, param_max=None):
        if not isinstance(param_value, int) or isinstance(param_value, bool):
            raise InvalidParameter(f'{param_name} ({param_value}) should be an integer')
        if param_min is not None and param_value < param_min:
            raise InvalidParameter(f'{param_name} ({param_value}) should be >= {param_min}')
        if param_max is not None and param_value > param_max:
            raise InvalidParameter(f'{param_name} ({param_value}) should be <= {param_max}')
        return int(param_value)

    def parse_string_param(param_name, param_value, allowed=None):
        if not isinstance(param_value, str):
            raise InvalidParameter(f'{param_name} ({param_value}) should be an string')
        if allowed is not None and param_value not in allowed:
            raise InvalidParameter(f'{param_name} ({param_value}) should be one of [{", ".join(allowed)}]')
        return str(param_value)

    def parse_boolean(param_name, param_value):
        if not isinstance(param_value, bool):
            raise InvalidParameter(f'{param_name} ({param_value}) should be boolean')
        return param_value

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
        damped = parse_boolean('damped', params['damped'])

    seasonal = None
    if 'seasonal' in params and params['seasonal'] is not None:
        seasonal = parse_string_param('seasonal', params['seasonal'], ['add', 'mul'])

    seasonal_periods = None
    if 'seasonal_periods' in params and params['seasonal_periods'] is not None:
        seasonal_periods = parse_integer_param('seasonal_periods', params['seasonal_periods'], param_min=1)

    if trend == 'mul' and initial_level == 0.0:
        raise InvalidParameter(f'initial level can not be {initial_level} if trend={trend}')
    if damped and not trend:
        raise InvalidParameter(f'trend must be provided if damped = {damped}')
    if phi is not None and not damped:
        raise InvalidParameter(f'damped must be True if phi = {phi}')

    if seasonal and seasonal_periods is None:
        raise InvalidParameter(f'seasonal_periods must be provided if seasonal = {seasonal}')
    if seasonal_periods is not None and seasonal is None:
        raise InvalidParameter(f'seasonal must be provided if seasonal_periods = {seasonal_periods}')
    if gamma is not None and seasonal is None:
        raise InvalidParameter(f'seasonal and seasonal_periods must be provided if gamma = {gamma}')

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

    return {
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


class HoltWinter:

    def __init__(self, parse_params):
        self._parse_params = parse_params

    def _parse_data(self, input_data):
        try:
            input_data = input_data.values
            input_data_length = input_data.shape[0]
        except Exception:
            input_data = np.array(input_data)
            input_data_length = len(input_data)
        return input_data, input_data_length

    def _create_model(self, input_data, params):
        return smholtwinter(
            input_data,
            trend=params.get('trend', None),
            damped=params.get('damped', None),
            seasonal=params.get('seasonal', None),
            seasonal_periods=params.get('seasonal_periods', None)
        )

    def _fit_model(self, model, params):
        return model.fit(
            smoothing_level=params.get('alpha', None),
            initial_level=params.get('initial_level', None),
            smoothing_slope=params.get('beta', None),
            initial_slope=params.get('initial_slope', None),
            smoothing_seasonal=params.get('gamma', None),
            damping_slope=params.get('phi', None),
            optimized=params.get('to_fit', True)
        )

    def _fit_params(self, fit, params):
        params['alpha'] = fit.params['smoothing_level']
        params['initial_level'] = fit.params['initial_level']
        params['beta'] = fit.params['smoothing_slope']
        params['initial_slope'] = fit.params['initial_slope']
        params['gamma'] = fit.params['smoothing_seasonal']
        params['phi'] = fit.params['damping_slope']
        params['initial_seasons'] = list(fit.params['initial_seasons'])
        return params

    def _forecast(self, fit, forecast_horizon):
        return fit.forecast(
            forecast_horizon
        )

    def _predict(self, model, start_index, end_index, params):
        return model.predict(
            {
                'smoothing_level': params.get('alpha', None),
                'initial_level': params.get('initial_level', None),
                'smoothing_slope': params.get('beta', None),
                'initial_slope': params.get('initial_slope', None),
                'smoothing_seasonal': params.get('gamma', None),
                'damping_slope': params.get('phi', None),
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

    import pandas as pd
    test_data = pd.Series([1.1, 1.9, 3.1, 3.9, 5.1, 3.9, 3.1, 1.9, 1.1, 2.1, 2.9, 4.1, 4.9, 4.1, 2.9, 2.1, 1, 2, 3, 4, 5, 4, 3, 2, 1])
    forecast_horizon = 1
    params = {
        'alpha': 0.05,
        'beta': 0.02,
        'gamma': 0.01,
        'initial_level': 0.9,
        'initial_slope': 0.5, # when trend dampening is on the initial slope isn't respected
        'trend': 'mul',
        'damped': True,
        'phi': 0.1,
        'seasonal_periods': 8,
        'seasonal': 'add',
    }
    hes = HoltWinter(parse_params)
    res = hes.fit_forecast(
        test_data,
        forecast_horizon,
        **params
    )
    print(res['forecast'])
    for key in sorted(res['params']):
        value = res['params'][key]
        print(f'{key} = {value}')

    #res = hes.forecast(
    #    test_data,
    #    forecast_horizon,
    #    **params
    #)
    #print(res)
