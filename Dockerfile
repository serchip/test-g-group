FROM python:3.11.3-slim as base

FROM base as app_builder
WORKDIR /src
RUN apt-get update \
    && apt-get --no-install-recommends install -y gcc g++ python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY ./poetry.lock /src/poetry.lock
COPY ./pyproject.toml /src/pyproject.toml
RUN pip install --no-cache-dir -U pip==23.1.2 poetry==1.4.2 \
    && python -m venv /env \
    && . /env/bin/activate \
    && poetry install --without dev,migrations

FROM app_builder as migrations
ARG VERSION
ENV VERSION ${VERSION:-0.0.0}
COPY --from=app_builder /env /env
RUN . /env/bin/activate \
    && poetry install --with migrations
COPY app /src/app
COPY migrations /src/migrations
COPY alembic.ini /src
ENV PYTHONPATH=/src
ENV PATH="/env/bin:${PATH}"
CMD ["alembic", "upgrade", "head"]

FROM app_builder as app
ARG VERSION
ENV VERSION ${VERSION:-0.0.0}
COPY --from=app_builder /env /env
COPY app /src/app

ENV PYTHONPATH=/src
ENV PATH="/env/bin:${PATH}"
EXPOSE 80
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:80", "--worker-class", "uvloop"]

FROM app_builder as pytests
ARG VERSION
ENV VERSION ${VERSION:-0.0.0}
COPY --from=app_builder /env /env
RUN . /env/bin/activate \
    && poetry install --with dev
COPY app /src/app
COPY tests /src/tests
ENV PYTHONPATH=/src
ENV PATH="/env/bin:${PATH}"
CMD ["pytest", "-q", "tests/"]
