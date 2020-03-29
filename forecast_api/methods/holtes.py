import numpy as np
from statsmodels.tsa.api import Holt as smholt


class Holt:

    def __init__(self):
        pass

    def _parse_params(self, **params):
        alpha = params.get('alpha', None)
        optimized_alpha = True
        if alpha:  # TODO what if this is zero??
            optimized_alpha = False
            alpha = float(alpha)
            if alpha < 0 or alpha > 1:
                raise ValueError(f'alpha ({alpha}) should be >= 0 and <= 1')

        initial_level = params.get('initial_level', None)
        optimized_initial_level = True
        if initial_level:  # TODO what if this is zero??
            optimized_initial_level = False
            initial_level = float(initial_level)
            if initial_level < 0:
                raise ValueError(f'initial_level ({initial_level}) should be >= 0')

        beta = params.get('beta', None)
        optimized_beta = True
        if beta:  # TODO what if this is zero??
            optimized_beta = False
            beta = float(beta)
            if beta < 0 or beta > 1:
                raise ValueError(f'beta ({beta}) should be >= 0 and <= 1')

        initial_slope = params.get('initial_slope', None)
        optimized_initial_slope = True
        if initial_slope:  #  TODO what if this is zero??
            optimized_initial_slope = False
            initial_slope = float(initial_slope)

        to_fit = False
        if optimized_alpha or optimized_initial_level or \
                optimized_beta or optimized_initial_slope:
            to_fit = True

        phi = params.get('phi', None)
        if phi:
            phi = float(phi)
        damped = params.get('damped', False)
        exponential = params.get('exponential', False)

        optimized_phi = False
        if not (exponential):
            phi = None
        if (exponential) and not phi:
            optimized_phi = True

        if not to_fit and optimized_phi:
            raise ValueError(f'phi should be set if exponential={exponential}')

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

    def _parse_data(self, input_data):
        try:
            input_data = input_data.values
            input_data_length = input_data.shape[0]
        except Exception:
            input_data = np.array(input_data)
            input_data_length = len(input_data)
        return input_data, input_data_length

    def _create_model(self, input_data, params):
        return smholt(
            input_data,
            exponential=params.get('exponential', None),
            damped=params.get('exponential', None)
        )

    def _fit_model(self, model, params):
        return model.fit(
            smoothing_level=params.get('alpha', None),
            initial_level=params.get('initial_level', None),
            smoothing_slope=params.get('beta', None),
            initial_slope=params.get('initial_slope', None),
            damping_slope=params.get('phi', None),
            optimized=params.get('to_fit', True)
        )

    def _fit_params(self, fit, params):
        params['alpha'] = fit.params['smoothing_level']
        params['initial_level'] = fit.params['initial_level']
        params['beta'] = fit.params['smoothing_slope']
        params['initial_slope'] = fit.params['initial_slope']
        params['phi'] = fit.params['damping_slope']
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
    test_data = pd.Series([8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8])
    forecast_horizon = 12
    params = {
#        'alpha': 0.0,
#        'initial_level': 50,
#        'beta': 0.02,
#        'initial_slope': 0.0,
#        'exponential': False,
#        'damped': False,
#        'phi': False
    }
    hes = Holt()
    res = hes.fit_forecast(
        test_data,
        forecast_horizon,
        **params
    )
    print(res)

    res = hes.forecast(
        test_data,
        forecast_horizon,
        **params
    )
    print(res)
