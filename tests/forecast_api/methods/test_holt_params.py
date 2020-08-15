import pytest

import numpy as np

from forecast_api.lib.exceptions import (
    InvalidBooleanParameter,
    InvalidNumericParameter,
)
from forecast_api.lib.exceptions import (
    InvalidTrendParameters,
)


# TODO Maybe think about using hypothesis here to generate these invalid values
valid_coefficient_values = list(np.arange(0, 1, 0.1))
valid_initial_level = list(np.arange(0, 10, 0.5))
valid_initial_slope = list(np.arange(-10, 10, 0.5))

base_invalid_values = ['string', 0.j, [], (), {}]
invalid_coefficient_values = base_invalid_values+[True, False, -1.1, -0.5, 1.1]
invalid_initial_level_values = base_invalid_values+[True, False, -1.1, -0.5]
invalid_initial_slope_values = base_invalid_values+[True, False]
invalid_exponential_values = base_invalid_values+[-1.1, -0.5, 1.1]
invalid_damped_values = base_invalid_values+[-1.1, -0.5, 1.1]


@pytest.fixture
def parse_params(container):
    def _parse_params(**kwargs):
        parse_params = container('services.methods.holt_parse_params')
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

    @pytest.mark.parametrize('exponential', invalid_exponential_values)
    def test_invalid_exponential(self,  parse_params, exponential):
        with pytest.raises(InvalidBooleanParameter):
            parse_params(**{'exponential': exponential})

    @pytest.mark.parametrize('damped', invalid_damped_values)
    def test_invalid_damped(self,  parse_params, damped):
        with pytest.raises(InvalidBooleanParameter):
            parse_params(**{'damped': damped})

    @pytest.mark.parametrize('phi', invalid_coefficient_values)
    def test_invalid_phi(self,  parse_params, phi):
        with pytest.raises(InvalidNumericParameter):
            parse_params(**{'phi': phi})

    @pytest.mark.parametrize('exponential', [False, None])
    def test_false_exponential(self,  parse_params, exponential):
        params = parse_params(
            **{
                'exponential': exponential,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('exponential', [False, None])
    @pytest.mark.parametrize('damped', [True])
    def test_false_exponential_with_damped(self,  parse_params, exponential, damped):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'exponential': exponential,
                    'damped': damped,
                }
            )

    @pytest.mark.parametrize('exponential', [False, None])
    @pytest.mark.parametrize('damped', [True])
    @pytest.mark.parametrize('phi', valid_coefficient_values)
    def test_false_exponential_with_damped_phi(self,  parse_params, exponential, damped, phi):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'exponential': exponential,
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

    @pytest.mark.parametrize('exponential', [True])
    @pytest.mark.parametrize('damped', [False, None])
    def test_false_damped_with_exponential(self,  parse_params, exponential, damped):
        params = parse_params(
            **{
                'exponential': exponential,
                'damped': damped,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('exponential', [True])
    @pytest.mark.parametrize('damped', [False, None])
    @pytest.mark.parametrize('phi', valid_coefficient_values)
    def test_false_damped_with_exponential_phi(self,  parse_params, exponential, damped, phi):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'exponential': exponential,
                    'damped': damped,
                    'phi': phi
                }
            )

    @pytest.mark.parametrize('exponential', [True])
    @pytest.mark.parametrize('damped', [True])
    @pytest.mark.parametrize('phi', [None])
    def test_none_phi(self,  parse_params, exponential, damped, phi):
        params = parse_params(
            **{
                'exponential': exponential,
                'damped': damped,
                'phi': phi
            }
        )
        assert params['phi'] == phi
        assert params['optimized_phi'] is True

    @pytest.mark.parametrize('exponential', [True, False])
    def test_valid_exponential(self,  parse_params, exponential):
        params = parse_params(
            **{
                'exponential': exponential,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('exponential', [True])
    @pytest.mark.parametrize('damped', [True])
    def test_valid_damped(self,  parse_params, exponential, damped):
        params = parse_params(
            **{
                'exponential': exponential,
                'damped': damped,
            }
        )
        assert params['phi'] is None
        assert params['optimized_phi'] is True

    @pytest.mark.parametrize('exponential', [True])
    @pytest.mark.parametrize('damped', [True])
    @pytest.mark.parametrize('phi', valid_coefficient_values)
    def test_valid_phi(self,  parse_params, exponential, damped, phi):
        params = parse_params(
            **{
                'exponential': exponential,
                'damped': damped,
                'phi': phi
            }
        )
        assert params['phi'] == phi
        assert params['optimized_phi'] is False

    @pytest.mark.parametrize('initial_level', [0, 0.0])
    @pytest.mark.parametrize('exponential', [True])
    def test_exponential_zero_initial_level(self,  parse_params, initial_level, exponential):
        with pytest.raises(InvalidTrendParameters):
            parse_params(
                **{
                    'exponential': exponential,
                    'initial_level': initial_level
                }
            )
