FROM ubuntu:20.04 AS base

WORKDIR /alfalfa-bacnet-bridge

RUN apt update \
    && apt install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock .
COPY pyproject.toml .

RUN ln -sf /usr/bin/python3 /usr/bin/python \
    && pip3 install poetry==1.8.3 \
    && poetry install --no-root --only main

COPY alfalfa_bacnet_bridge alfalfa_bacnet_bridge

ENV TERM=xterm

CMD poetry run python alfalfa_bacnet_bridge/alfalfa_watchdog.py alfalfa_bacnet_bridge/alfalfa_bacnet_bridge.py

FROM base AS cli

COPY cli/cli_setup.py .

CMD poetry run python -i cli_setup.py
