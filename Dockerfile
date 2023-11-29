FROM python:3.11-slim as base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV="/venv"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

WORKDIR /app
COPY pyproject.toml poetry.lock ./


FROM base as pydeps

RUN pip install "poetry==1.7.1" && \
    python -m venv ${VIRTUAL_ENV}

RUN poetry install --only=main --extras=textract --no-interaction


FROM base as final

ENV ORGANIZE_CONFIG=/config/config.yml

RUN mkdir /config && touch ./README.md
COPY --from=pydeps ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY ./organize ./organize
RUN python -m pip install .

ENTRYPOINT ["organize"]
