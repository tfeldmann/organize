# based on https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
FROM python:3.8-alpine3.11 as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /tmp

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.0.2

RUN apk add --no-cache gcc libffi-dev musl-dev openssl-dev libxml2-dev libxslt-dev libjpeg-turbo-dev
RUN pip install "poetry==$POETRY_VERSION"

RUN python -m venv /app

COPY pyproject.toml poetry.lock README.md ./
RUN mkdir organize && touch organize/__init__.py

RUN poetry config virtualenvs.create false && \
    poetry config virtualenvs.path /app && \
    poetry install

COPY . .
RUN poetry run pytest -vv
RUN poetry build && /app/bin/pip install dist/*.whl

FROM base as final
WORKDIR /app

RUN apk add --no-cache libffi openssl-dev libxml2-dev libxslt libjpeg-turbo
COPY --from=builder /app /app
COPY docker-entrypoint.sh /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
