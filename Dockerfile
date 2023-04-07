FROM python:3.10.4-bullseye
ENV POETRY_VERSION=1.1.13 POETRY_HOME=/poetry
ENV PATH=/poetry/bin:$PATH
LABEL maintainer="sigae@protonmail.com"
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY . /app
WORKDIR /app/src
RUN poetry install --no-dev
CMD poetry run python main.py