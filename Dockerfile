# Image: python:3.11-slim-bullseye linux/amd64.
FROM python@sha256:0e8fdea6c80a023af4726ecbcfb245d9ea5b2f46b18dc3a5f086a97edf17c15f AS python-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ARG POETRY_GROUPS
ARG DEV=false
ENV DEV $DEV

FROM python-base AS python-builder

RUN apt-get update && \
    apt-get install -y git wget && \
    if [ "$DEV" = "false" ]; then \
        apt-get install -y --no-install-recommends gcc libpq-dev python3-dev; \
    fi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip \
    && pip install "poetry==$POETRY_VERSION"

WORKDIR $PYSETUP_PATH

# SSH Config
RUN mkdir /root/.ssh/ \
    && ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 400 /root/.ssh/id_rsa

RUN wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -P /root/


COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    if [ "$DEV" = "true" ] ; \
    then poetry install --with="$POETRY_GROUPS" --no-root ; \
    else poetry install --no-root --only main,psycopg2,iris,reconciliation-execution-listener ; \
    fi

FROM python-base AS python-app

RUN apt-get update && apt-get install -y libpq5 && apt-get clean

RUN useradd app
USER app
COPY --from=python-builder --chown=app $VENV_PATH $VENV_PATH
COPY --from=python-builder --chown=app /root/global-bundle.pem /app/
COPY --chown=app . /app

RUN . "$VENV_PATH/bin/activate"
WORKDIR /app

EXPOSE 8000