FROM python:3.11-slim as base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV="/venv"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
WORKDIR /app


FROM base as pydeps

RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv venv ${VIRTUAL_ENV} && \
    uv pip compile --generate-hashes pyproject.toml > requirements.txt && \
    uv pip install --require-hashes -r requirements.txt
RUN uv pip freeze

FROM base as final

RUN apt update && \
    apt install -y exiftool poppler-utils && \
    rm -rf /var/lib/apt/lists/*
ENV ORGANIZE_CONFIG=/config/config.yml \
    ORGANIZE_EXIFTOOL_PATH=exiftool
RUN mkdir /config && mkdir /data
COPY --from=pydeps ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY ./organize ./organize

ENTRYPOINT ["python", "-m", "organize"]
CMD ["--help"]
