import pytest
import webtest

from forecast_api.wsgi import create_callable
from forecast_api.app import create_container


@pytest.fixture
def container(request):
    return create_container(
        request.config.getoption(
            'ini_file'
        )
    )


@pytest.fixture
def app(container):
    return create_callable(container)


@pytest.fixture
def webapi(app):
    return webtest.TestApp(app)


@pytest.fixture
def fresh_schema(request):
    from alembic.command import downgrade, upgrade
    from alembic.config import Config

    cfg = Config(request.config.getoption('ini_file'))

    downgrade(cfg, 'base')
    upgrade(cfg, 'head')


def pytest_addoption(parser):
    parser.addoption(
        '--ini-file',
        action='store',
        type='string',
        default='forecast_api/confs/testing.ini',
        help=(
            'INI file path, i.e.: forecast_api/confs/testing.ini'
        )
    )
