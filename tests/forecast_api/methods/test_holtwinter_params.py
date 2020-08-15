import pytest

import numpy as np

from forecast_api.lib.exceptions import (
    InvalidBooleanParameter,
    InvalidIntegerParameter,
    InvalidNumericParameter,
    InvalidStringParameter,
)
from forecast_api.lib.exceptions import (
    InvalidSeasonalParameters,
    InvalidTrendParameters,
)


valid_coefficient_values = list(np.arange(0, 1, 0.1))
valid_initial_level = list(np.arange(0, 10, 0.5))
valid_initial_slope = list(np.arange(-10, 10, 0.5))
valid_seasonal_values = ['add', 'mul']
valid_seasonal_period_values = [1, 4, 7, 12, 52]

base_invalid_values = ['string', 0.j, [], (), {}]
invalid_coefficient_values = base_invalid_values+[True, False, -1.1, -0.5, 1.1]
invalid_initial_level_values = base_invalid_values+[True, False, -1.1, -0.5]
invalid_initial_slope_values = base_invalid_values+[True, False]
invalid_trend_values = base_invalid_values+['notadd', 'notmul', True, False, -1.1, -0.5, 1.1]
invalid_damped_values = base_invalid_values+[-1.1, -0.5, 1.1]
invalid_seasonal_values = base_invalid_values+['notadd', 'notmul', True, False, -1.1, -0.5, 1.1]
invalid_seasonal_period_values = base_invalid_values+[True, False, -1.1, -0.5, 1.1, 0, -1]


# TODO Maybe think about using hypothesis here to generate these invalid values
@pytest.fixture
def parse_params(container):
    def _parse_params(**kwargs):
        parse_params = container('services.methods.holtwinter_parse_params')
        return parse_params(**kwargs)
    return _parse_params


class TestIndependentCoefficientParameters:

    @pytest.mark.parametrize('coefficient_name', ['alpha', 'beta'])
    @pytest.mark.parametrize('coefficient_value', invalid_coefficient_values)
    def test_invalid_coefficients(self, parse_params, coefficient_name, coefficient_value):

        with pytest.raises(InvalidNumericParameter):
            parse_params(
                **{
                    coefficient_name: coefficient_value
                }
            )

    @pytest.mark.parametrize('coefficient_name', ['alpha', 'beta'])
    @pytest.mark.parametrize('coefficient_value', [None])
    def test_none_coefficients(self,  parse_params, coefficient_name, coefficient_value):
        params = parse_params(
            **{
                coefficient_name: coefficient_value
            }
        )
        assert params[coefficient_name] == coefficient_value
        assert params[f'optimized_{coefficient_name}'] is True

    @pytest.mark.parametrize('coefficient_name', ['alpha', 'beta'])
    @pytest.mark.parametrize('coefficient_value', valid_coefficient_values)
    def test_valid_coefficients(self,  parse_params, coefficient_name, coefficient_value):
        params = parse_params(
            **{
                coefficient_name: coefficient_value
            }
        )
        assert params[coefficient_name] == coefficient_value
        assert params[f'optimized_{coefficient_name}'] is False


class TestLevelParameters:

    @pytest.mark.parametrize('initial_level', invalid_initial_level_values)
    def test_invalid_initial_level(self,  parse_params, initial_level):
        with pytest.raises(InvalidNumericParameter):
            parse_params(**{'initial_level': initial_level})

    @pytest.mark.parametrize('initial_level', [None])
    def test_none_initial_level(self,  parse_params, initial_level):
        params = parse_params(
            **{
                'initial_level': initial_level
            }
        )
        assert params['initial_level'] is None
        assert params['optimized_initial_level'] is True

    @pytest.mark.parametrize('initial_level', valid_initial_level)
    def test_valid_initial_level(self,  parse_params, initial_level):
        params = parse_params(
            **{
                'initial_level': initial_level
            }
        )
        assert params['initial_level'] == initial_level
        assert params['optimized_initial_level'] is False

    @pytest.mark.parametrize('initial_slope', invalid_initial_slope_values)
    def test_invalid_initial_slope(self,  parse_params, initial_slope):
        with pytest.raises(InvalidNumericParameter):
            parse_params(**{'initial_slope': initial_slope})

    @pytest.mark.parametrize('initial_slope', [None])
    def test_none_initial_level(self,  parse_params, initial_slope):
        params = parse_params(
            **{
                'initial_slope': initial_slope
            }
        )
        assert params['initial_slope'] is None
        assert params['optimized_initial_slope'] is True

    @pytest.mark.parametrize('initial_slope', valid_initial_slope)
    def test_valid_initial_slope(self,  parse_params, initial_slope):
        params = parse_params(
            **{
                'initial_slope': initial_slope
            }
        )
        assert params['initial_slope'] == initial_slope
        assert params['optimized_initial_slope'] is False


class TestTrendParameters:

    @pytest.mark.parametrize('trend', invalid_trend_values)
    def test_invalid_trend(self,  parse_params, trend):
        with pytest.raises(InvalidStringParameter):
            parse_params(**{'trend': trend})

    @pytest.mark.parametrize('damped', invalid_damped_values)
    def test_invalid_damped(self,  parse_params, damped):
        with pytest.raises(InvalidBooleanParameter):
            parse_params(**{'damped': damped})

    @pytest.mark.parametrize('phi', invalid_coefficient_values)
    def test_invalid_phi(self,  parse_params, phi):
        with pytest.raises(InvalidNumericParameter):
            parse_params(**{'phi': phi})

    @pytest.mark.parametrize('trend', [None])
    def test_none_trend(self,  parse_params, trend):
        params = parse_params(
            **{
                'trend': trend,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('trend', [None])
    @pytest.mark.parametrize('damped', [True])
    def test_none_trend_with_damped(self,  parse_params, trend, damped):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'trend': trend,
                    'damped': damped,
                }
            )

    @pytest.mark.parametrize('trend', [None])
    @pytest.mark.parametrize('damped', [True])
    @pytest.mark.parametrize('phi', valid_coefficient_values)
    def test_none_trend_with_damped_phi(self,  parse_params, trend, damped, phi):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'trend': trend,
                    'damped': damped,
                    'phi': phi
                }
            )

    @pytest.mark.parametrize('damped', [False, None])
    def test_false_damped(self,  parse_params, damped):
        params = parse_params(
            **{
                'damped': damped,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('trend', ['add', 'mul'])
    @pytest.mark.parametrize('damped', [False, None])
    def test_false_damped_with_trend(self,  parse_params, trend, damped):
        params = parse_params(
            **{
                'trend': trend,
                'damped': damped,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('trend', ['add', 'mul'])
    @pytest.mark.parametrize('damped', [False, None])
    @pytest.mark.parametrize('phi', valid_coefficient_values)
    def test_false_damped_with_trend_phi(self,  parse_params, trend, damped, phi):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'trend': trend,
                    'damped': damped,
                    'phi': phi
                }
            )

    @pytest.mark.parametrize('trend', ['add', 'mul'])
    @pytest.mark.parametrize('damped', [True])
    @pytest.mark.parametrize('phi', [None])
    def test_none_phi(self,  parse_params, trend, damped, phi):
        params = parse_params(
            **{
                'trend': trend,
                'damped': damped,
                'phi': phi
            }
        )
        assert params['phi'] == phi
        assert params['optimized_phi'] is True

    @pytest.mark.parametrize('trend', ['add', 'mul'])
    def test_valid_trend(self,  parse_params, trend):
        params = parse_params(
            **{
                'trend': trend,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('trend', ['add', 'mul'])
    @pytest.mark.parametrize('damped', [True])
    def test_valid_trend_damped(self,  parse_params, trend, damped):
        params = parse_params(
            **{
                'trend': trend,
                'damped': damped,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is True

    @pytest.mark.parametrize('trend', ['add', 'mul'])
    @pytest.mark.parametrize('damped', [True])
    @pytest.mark.parametrize('phi', valid_coefficient_values)
    def test_valid_phi(self,  parse_params, trend, damped, phi):
        params = parse_params(
            **{
                'trend': trend,
                'damped': damped,
                'phi': phi
            }
        )
        assert params['phi'] == phi
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('initial_level', [0, 0.0])
    @pytest.mark.parametrize('trend', ['mul'])
    def test_mul_trend_zero_initial_level(self,  parse_params, initial_level, trend):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'trend': trend,
                    'initial_level': initial_level
                }
            )


class TestSeasonalParameters:

    @pytest.mark.parametrize('seasonal', invalid_seasonal_values)
    def test_invalid_seasonal(self,  parse_params, seasonal):
        with pytest.raises(InvalidStringParameter):
            parse_params(**{'seasonal': seasonal})

    @pytest.mark.parametrize('seasonal_periods', invalid_seasonal_period_values)
    def test_invalid_seasonal_periods(self,  parse_params, seasonal_periods):
        with pytest.raises(InvalidIntegerParameter):
            parse_params(**{'seasonal_periods': seasonal_periods})

    @pytest.mark.parametrize('gamma', invalid_coefficient_values)
    def test_invalid_gamma(self,  parse_params, gamma):
        with pytest.raises(InvalidNumericParameter):
            parse_params(**{'gamma': gamma})

    @pytest.mark.parametrize('seasonal', [None])
    def test_none_seasonal(self,  parse_params, seasonal):
        params = parse_params(
            **{
                'seasonal': seasonal,
            }
        )
        assert params['gamma'] is None
        assert params['optimized_gamma'] is False
        assert params['optimized_seasonal'] is False

    @pytest.mark.parametrize('seasonal', [None])
    @pytest.mark.parametrize('seasonal_periods', valid_seasonal_period_values)
    def test_none_seasonal_with_seasonal_periods(self,  parse_params, seasonal, seasonal_periods):
        with pytest.raises(InvalidSeasonalParameters):
            parse_params(
                **{
                    'seasonal': seasonal,
                    'seasonal_periods': seasonal_periods,
                }
            )

    @pytest.mark.parametrize('seasonal', [None])
    @pytest.mark.parametrize('seasonal_periods', valid_seasonal_period_values)
    @pytest.mark.parametrize('gamma', valid_coefficient_values)
    def test_none_seasonal_with_seasonal_periods_gamma(self,  parse_params, seasonal, seasonal_periods, gamma):
        with pytest.raises(InvalidSeasonalParameters):
            parse_params(
                **{
                    'seasonal': seasonal,
                    'seasonal_periods': seasonal_periods,
                    'gamma': gamma
                }
            )

    @pytest.mark.parametrize('seasonal', valid_seasonal_values)
    @pytest.mark.parametrize('seasonal_periods', [None])
    def test_none_seasonal_periods_with_seasonal(self,  parse_params, seasonal, seasonal_periods):
        with pytest.raises(InvalidSeasonalParameters):
            parse_params(
                **{
                    'seasonal': seasonal,
                    'seasonal_periods': seasonal_periods,
                }
            )

    @pytest.mark.parametrize('seasonal', valid_seasonal_values)
    @pytest.mark.parametrize('seasonal_periods', [None])
    @pytest.mark.parametrize('gamma', valid_coefficient_values)
    def test_none_seasonal_periods_with_seasonal_gamma(self,  parse_params, seasonal, seasonal_periods, gamma):
        with pytest.raises(InvalidSeasonalParameters):
            parse_params(
                **{
                    'seasonal': seasonal,
                    'seasonal_periods': seasonal_periods,
                    'gamma': gamma
                }
            )

    @pytest.mark.parametrize('seasonal', valid_seasonal_values)
    @pytest.mark.parametrize('seasonal_periods', valid_seasonal_period_values)
    def test_valid_seasonal_seasonal_periods(self,  parse_params, seasonal, seasonal_periods):
        params = parse_params(
            **{
                'seasonal': seasonal,
                'seasonal_periods': seasonal_periods,
            }
        )
        assert params['gamma'] is None
        assert params['optimized_gamma'] is True
        assert params['optimized_seasonal'] is True

    @pytest.mark.parametrize('seasonal', valid_seasonal_values)
    @pytest.mark.parametrize('seasonal_periods', valid_seasonal_period_values)
    @pytest.mark.parametrize('gamma', valid_coefficient_values)
    def test_valid_seasonal_seasonal_periods_gamma(self,  parse_params, seasonal, seasonal_periods, gamma):
        params = parse_params(
            **{
                'seasonal': seasonal,
                'seasonal_periods': seasonal_periods,
                'gamma': gamma
            }
        )
        assert params['gamma'] == gamma
        assert params['optimized_gamma'] is False
        assert params['optimized_seasonal'] is True
