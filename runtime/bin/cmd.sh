#!/usr/bin/env bash

# set defaults
GUNICORN_PORT="${LISTEN_PORT:-80}"
GUNICORN_GRACEFUL_TIMEOUT="${GUNICORN_GRACEFUL_TIMEOUT:-60}"
GUNICORN_MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-100000}"
GUNICORN_MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-20000}"
GUNICORN_WORKER_CLASS="${GUNICORN_WORKER_CLASS:-sync}"
GUNICORN_NUM_WORKERS="${GUNICORN_NUM_WORKERS:-2}"
GUNICORN_NUM_THREADS="${GUNICORN_NUM_THREADS:-5}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-60}"

exec "gunicorn" \
    --bind ":${GUNICORN_PORT}" \
    --timeout ${GUNICORN_TIMEOUT} \
    --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT} \
    --max-requests ${GUNICORN_MAX_REQUESTS} \
    --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER} \
    --worker-class ${GUNICORN_WORKER_CLASS} \
    --workers ${GUNICORN_NUM_WORKERS} \
    --limit-request-field_size 0 \
    --threads ${GUNICORN_NUM_THREADS} \
    -c "${APP_HOME_DIR}/conf/gunicorn.config.py" \
    sessionsvc:create_app\(\)
