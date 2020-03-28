#!/usr/bin/env bash
wait-for-it.sh forecast_api-postgres-dev:5432
alembic -c forecast_api/confs/docker_dev.ini upgrade head
uwsgi --ini=forecast_api/confs/docker_dev.ini
