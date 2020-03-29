#!/usr/bin/env bash
py.test --ini-file=forecast_api/confs/testing.ini --cov forecast_api --cov-report term-missing
