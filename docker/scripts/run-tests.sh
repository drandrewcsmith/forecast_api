#!/usr/bin/env bash
pytest --ini-file=forecast_api/confs/testing.ini --pep8 --cov forecast_api --cov-report term-missing
