from forecast_api.lib.exceptions import (
    InvalidBooleanParameter,
    InvalidIntegerParameter,
    InvalidNumericParameter,
    InvalidStringParameter,
)


def parse_numeric_param(param_name, param_value, param_min=None, param_max=None):
    if not isinstance(param_value, (int, float)) or isinstance(param_value, bool):
        raise InvalidNumericParameter(f'{param_name} ({param_value}) should be a real number (got {type(param_value)})')
    if param_min is not None and param_value < param_min:
        raise InvalidNumericParameter(f'{param_name} ({param_value}) should be >= {param_min}')
    if param_max is not None and param_value > param_max:
        raise InvalidNumericParameter(f'{param_name} ({param_value}) should be <= {param_max}')
    return float(param_value)


def parse_integer_param(param_name, param_value, param_min=None, param_max=None):
    if not isinstance(param_value, int) or isinstance(param_value, bool):
        raise InvalidIntegerParameter(f'{param_name} ({param_value}) should be an integer (got {type(param_value)})')
    if param_min is not None and param_value < param_min:
        raise InvalidIntegerParameter(f'{param_name} ({param_value}) should be >= {param_min}')
    if param_max is not None and param_value > param_max:
        raise InvalidIntegerParameter(f'{param_name} ({param_value}) should be <= {param_max}')
    return int(param_value)


def parse_string_param(param_name, param_value, allowed=None):
    if not isinstance(param_value, str):
        raise InvalidStringParameter(f'{param_name} ({param_value}) should be an string (got {type(param_value)})')
    if allowed is not None and param_value not in allowed:
        raise InvalidStringParameter(f'{param_name} ({param_value}) should be one of [{", ".join(allowed)}]')
    return str(param_value)


def parse_boolean_param(param_name, param_value):
    if not isinstance(param_value, bool):
        raise InvalidBooleanParameter(f'{param_name} ({param_value}) should be boolean (got {type(param_value)})')
    return param_value
