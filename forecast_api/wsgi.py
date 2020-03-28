import os

import falcon
from configparser import ConfigParser
from sqlalchemy import engine_from_config

from forecast_api.api.ping import PingResource


def configure_callable(ini_path=None):
    engine = read_configuration(ini_path)

    return create_callable(engine)


def read_configuration(ini_path=None):
    ini_path = (
        ini_path
        if ini_path is not None
        else os.environ['FORECAST_API_CONFIG']
    )

    config = ConfigParser()
    config.read(ini_path)

    return engine_from_config(config['forecast_api'], 'sqlalchemy.')


def create_callable(engine):
    app = falcon.API()
    app.add_route('/alert/ping', PingResource(engine))

    return app
