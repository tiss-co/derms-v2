#!/usr/bin/env bash

./docker/docker-init.sh

## --max-requests
# The maximum number of requests that worker will handle before being gracefully
# restarted, could prevent memory leaks.
# (help: https://stackoverflow.com/a/24656069)

## --max-requests-jitter
# The maximum jitter to add to the `max-requests` setting. The jitter causes the
# restart per worker to be randomized by randint(0, max_requests_jitter). This is
# intended to avoid all workers restarting at the same time.
# (help: https://docs.rhodecode.com/RhodeCode-Enterprise/admin/tuning-gunicorn.html)

## --worker-class
# `gevent` worker class is much more preferable than the `eventlet` worker class.
# (help: https://stackoverflow.com/questions/42948547)
# (help: https://github.com/apache/superset/blob/1.2/docs/installation.rst#a-proper-wsgi-http-server)

## --access-logfile
# (help: https://stackoverflow.com/a/67125218)

## findings
# for n-core cpu -> suggested worker n, suggested threads 4*n.

HYPHEN_SYMBOL='-'
gunicorn \
    --bind "${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-8088}" \
    --log-level "${LOG_LEVEL:-warning}" \
    --access-logfile "${ACCESS_LOG_FILE:-None}" \
    --error-logfile "${ERROR_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --preload \
    --max-requests ${SERVER_WORKER_MAX_REQUESTS:-128} \
    --max-requests-jitter ${SERVER_WORKER_MAX_REQUESTS_JITTER:-32} \
    --workers ${SERVER_WORKER_AMOUNT:-1} \
    --worker-class ${SERVER_WORKER_CLASS:-gthread} \
    --threads ${SERVER_THREADS_AMOUNT:-1} \
    --limit-request-line ${SERVER_LIMIT_REQUEST_LINE:-0} \
    --limit-request-field_size ${SERVER_LIMIT_REQUEST_FIELD_SIZE:-0} \
    "${FLASK_APP}"
