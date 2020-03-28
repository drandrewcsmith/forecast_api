import pytest
import webtest

from forecast_api.wsgi import create_callable, read_configuration


@pytest.fixture(scope='session')
def db_engine(request):
    return read_configuration(request.config.getoption('ini_file'))


@pytest.fixture
def app(db_engine):
    return create_callable(db_engine)


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
