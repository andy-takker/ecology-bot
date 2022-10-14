FROM python:3.10-slim

RUN apt update && apt install -y --no-install-recommends build-essential wget unzip libssl-dev libffi-dev python-dev tzdata && rm -rf /var/lib/apt/lists/*
ENV TZ="Europe/Moscow"
RUN python3 -m pip install -U pip
COPY ./requirements.txt ./
RUN python3 -m pip install --no-deps -r requirements.txt

WORKDIR /bot

COPY ./alembic.ini /bot/
COPY ./ecology_bot /bot/ecology_bot
