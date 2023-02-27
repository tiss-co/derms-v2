#!/usr/bin/env bash

set -eo pipefail

if [[ "${1}" == "app" ]]; then
  echo "Starting web app..."
  flask run -p 8088 --with-threads --reload --debugger --host=0.0.0.0
elif [[ "${1}" == "app-gunicorn" ]]; then
  echo "Starting web app..."
  sleep 10
  /app/docker/docker-entrypoint.sh
fi
