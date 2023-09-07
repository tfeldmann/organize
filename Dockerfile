FROM python:3.11-slim as base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.5.1 \
    VIRTUAL_ENV="/venv" \
    PATH="${VIRTUAL_ENV}/bin:$PATH"

WORKDIR /app


FROM base as pydeps

RUN pip install "poetry==${POETRY_VERSION}" && \
    python -m venv ${VIRTUAL_ENV}

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --compile --only=main --extras=textract --no-root


FROM base as final

ENV PATH="${VIRTUAL_ENV}/bin:$PATH" \
    ORGANIZE_CONFIG=/config/config.yml

RUN mkdir /config
COPY --from=pydeps ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY . .

ENTRYPOINT ["/usr/bin/bash"]
