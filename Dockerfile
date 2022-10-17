# syntax=docker/dockerfile:1
FROM python:3.10.8-slim as base

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

FROM base as dev

COPY . .
ENTRYPOINT [ "python", "-m", "pytest" ]
