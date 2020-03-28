==================
forecast_api
==================

A single interface to generate timeseries forecasts


Docker install and development
==========

#. Prerequisites
    * Docker: https://docs.docker.com/engine/installation/
    * Docker Compose: https://docs.docker.com/compose/install/

#. Run tests locally
    .. code-block:: bash

      $ cd docker
      $ docker-compose run --rm tests

    Always use --rm flag to remove tests container after it has done it's job

#. Run development instance of api
    .. code-block:: bash

      $ cd docker
      $ docker-compose up app

    To confirm that it is up and running visit: http://localhost:8000/alert/ping


Native install and development
==========

#. Install the package:
    .. code-block:: bash

      $ pip install -e .

#. Install the packages for testing
    .. code-block:: bash

      $ pip install -r requirements_dev.txt

#. Run tests locally
    .. code-block:: bash

      $ py.test
   
#. Run development instance of api
    .. code-block:: bash

      $ uwsgi --ini=forecast_api/confs/development.ini

