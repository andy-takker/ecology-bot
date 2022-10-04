FROM python:3.10-slim

RUN apt update && apt install -y --no-install-recommends build-essential wget unzip libssl-dev libffi-dev python-dev tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ="Europe/Moscow"
RUN python3 -m pip install -U pip

RUN python3 -m pip install poetry

WORKDIR /bot

COPY pyproject.toml alembic.ini /bot/
RUN poetry config virtualenvs.create false --local


RUN poetry install

COPY ./ecology_bot ./ecology_bot
