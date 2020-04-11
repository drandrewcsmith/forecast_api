import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing as smholtwinter
from forecast_api.methods.exceptions import InvalidParameter


def parse_params(**params):
    try:
        alpha = params['alpha']
        alpha = float(alpha)
        if alpha < 0 or alpha > 1:
            raise InvalidParameter(f'alpha ({alpha}) should be >= 0 and <= 1')
        optimized_alpha = False
    except KeyError:
        optimized_alpha = True
        alpha = None
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'alpha ({alpha}) {e}')

    try:
        initial_level = params['initial_level']
        initial_level = float(initial_level)
        if initial_level < 0:
            raise InvalidParameter(f'initial_level ({initial_level}) should be >= 0')
        optimized_initial_level = False
    except KeyError:
        optimized_initial_level = True
        initial_level = None
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'initial_level ({initial_level}) {e}')

    try:
        beta = params['beta']
        beta = float(beta)
        if beta < 0 or beta > 1:
            raise InvalidParameter(f'beta ({beta}) should be >= 0 and <= 1')
        optimized_beta = False
    except KeyError:
        optimized_beta = True
        beta = None
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'beta ({beta}) {e}')

    try:
        initial_slope = params['initial_slope']
        initial_slope = float(initial_slope)
        optimized_initial_slope = False
    except KeyError:
        optimized_initial_slope = True
        initial_slope = None
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'initial_slope ({initial_slope}) {e}')

    try:
        gamma = params['gamma']
        gamma = float(gamma)
        if gamma < 0 or gamma > 1:
            raise InvalidParameter(f'gamma ({gamma}) should be >= 0 and <= 1')
        optimized_gamma = False
    except KeyError:
        gamma = None
        optimized_gamma = True
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'gamma ({gamma}) {e}')

    trend = params.get('trend', None)
    if trend and trend not in ['add', 'mul']:
        raise InvalidParameter(f'trend ({trend}) should be either "add" or "mul"')

    damped = params.get('damped', False)
    if not isinstance(damped, bool):
        raise InvalidParameter(f'damped ({damped}) should be boolean')

    try:
        phi = params['phi']
        phi = float(phi)
        if phi < 0 or phi > 1:
            raise InvalidParameter(f'phi ({phi}) should be >= 0 and <= 1')
        optimized_phi = False
    except KeyError:
        phi = None
        optimized_phi = True
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'phi ({phi}) {e}')

    if not trend or not damped:
        phi = None
        optimized_phi = False
        damped = False

    seasonal = params.get('seasonal', None)
    if seasonal and seasonal not in ['add', 'mul']:
        raise InvalidParameter(f'seasonal ({seasonal}) should be either "add" or "mul"')

    try:
        seasonal_periods = int(params['seasonal_periods'])
        if seasonal_periods <= 0 :
            raise InvalidParameter(f'seasonal_periods ({seasonal_periods}) should be > 0')
        optimized_seasonal = True
    except KeyError:
        seasonal_periods = None
        optimized_seasonal = False
    except (TypeError, ValueError) as e:
        raise InvalidParameter(f'seasonal_periods ({seasonal_periods}) {e}')

    # initial_seasons = params.get('initial_seasons', None)
    # if initial_seasons and isinstance(initial_seasons, list) and len(initial_seasons) != seasonal_periods:
    #     raise InvalidParameter(f'initial_seasons ({initial_seasons} is not the length of seasonal_periods ({seasonal_periods})')
    # if initial_seasons:
    #     optimized_seasonal = False

    to_fit = False
    if optimized_alpha or optimized_initial_level or optimized_beta or \
            optimized_initial_slope or optimized_seasonal or optimized_gamma or optimized_phi:
        to_fit = True

    if trend == 'mul' and initial_level == 0.0:
        raise InvalidParameter(f'initial level can not be {initial_level} if trend={trend}')

    return {
        'alpha': alpha,
        'initial_level': initial_level,
        'beta': beta,
        'initial_slope': initial_slope,
        'gamma': gamma,
        'phi': phi,
        'trend': trend,
        'damped': damped,
        'seasonal': seasonal,
        'seasonal_periods': seasonal_periods,
        # 'initial_seasons': initial_seasons,
        'to_fit': to_fit,
        'optimized_alpha': optimized_alpha,
        'optimized_initial_level': optimized_initial_level,
        'optimized_beta': optimized_beta,
        'optimized_initial_slope': optimized_initial_slope,
        'optimized_phi': optimized_phi,
        'optimized_gamma': optimized_gamma,
        'optimized_seasonal': optimized_seasonal
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
        # TODO: Pass the initial seasonal factors in the start params
        """"
        initial_seasons = params.get('initial_seasons', None)
        start_params = None
        if initial_seasons:
            start_params = [
                params.get('alpha', None),
                params.get('beta', None),
                params.get('gamma', None),
                params.get('initial_level', None),
                params.get('initial_slope', None),
                params.get('phi', None)
            ]
            start_params.extend(
                initial_seasons
            )
            start_params = np.array(start_params)
        """

        return model.fit(
            smoothing_level=params.get('alpha', None),
            initial_level=params.get('initial_level', None),
            smoothing_slope=params.get('beta', None),
            initial_slope=params.get('initial_slope', None),
            smoothing_seasonal=params.get('gamma', None),
#            start_params=start_params,
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
