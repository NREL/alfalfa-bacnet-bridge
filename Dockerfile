FROM ubuntu:20.04 as base

WORKDIR /alfalfa-bacnet-bridge

RUN apt update \
    && apt install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock .
COPY pyproject.toml .

RUN ln -sf /usr/bin/python3 /usr/bin/python \
    && pip3 install poetry==1.3.2 \
    && poetry install --no-root --only main

COPY alfalfa_bacnet_bridge alfalfa_bacnet_bridge
COPY BACpypes.ini .
COPY cli_setup.py .

ENV TERM=xterm