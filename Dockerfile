# define the global arguments
ARG PYTHON_VERSION=3.8


######################################################################
# base stage that simply does a pip install on our requirements
######################################################################

# base image
FROM python:${PYTHON_VERSION} as base

# set the environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set the working directory
WORKDIR /src

# copy the requirements.txt file
COPY requirements.txt .

# build Wheel archives for requirements
RUN python -m pip wheel --no-cache-dir --no-deps --wheel-dir /src/wheels -r requirements.txt

######################################################################
# final lean image
######################################################################

# base image
FROM python:${PYTHON_VERSION}-slim

# set the environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONPATH="/app" \
    FLASK_APP="wsgi:app" \
    FLASK_ENV="production" \
    FLASK_HOST="0.0.0.0" \
    FLASK_PORT=8088

# set the working directory
WORKDIR /app

# copy the dependency wheels from base image
COPY --from=base /src/wheels ./wheels
COPY bin ./wheels

# install the requirements
RUN python -m pip install --no-cache-dir ./wheels/*.whl

# copy the resources
COPY backend ./backend
COPY docker ./docker
COPY migrations ./migrations
COPY wsgi.py ./


# configure the permissions
RUN find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && find /app/docker/*.sh -type f -exec chmod 755 {} \;

# expose the port
EXPOSE ${FLASK_PORT}

# set the entrypoint
ENTRYPOINT ["/app/docker/docker-bootstrap.sh", "app-gunicorn"]
