#!/usr/bin/env bash
wait-for-it.sh forecast_api-postgres-tests:5432 -- alembic -c forecast_api/confs/testing.ini upgrade head
py.test --ini-file=forecast_api/confs/testing.ini --cov forecast_api --cov-report term-missing
