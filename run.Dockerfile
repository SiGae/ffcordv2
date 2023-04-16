FROM python:3.10
LABEL maintainer="sigae@protonmail.com"
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
RUN mkdir ffocrd
COPY . ffcord
WORKDIR ffcord/src
RUN poetry install
CMD poetry run python main.py
