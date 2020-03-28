#!/usr/bin/env bash
EGGDIR="forecast_api.egg-info"

if [ -d "$EGGDIR" ]; then
    rm -rf ${EGGDIR}
fi

echo 'Building development egg'
pip3 install -q --upgrade setuptools
pip3 install -q -e . 
pip3 install -q -r requirements_dev.txt

"$@"  # execute command passed to script
