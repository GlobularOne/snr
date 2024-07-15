FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
        make \
        git \
        clang \
        lld \
        nasm \
        curl \
        python3 \
        fakeroot \
        fakechroot \
        debootstrap


RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . /app

ENV POETRY_VIRTUALENVS_CREATE=false

RUN ./tools/build_payloads.sh && poetry install --only=main

RUN snr --init --init-only --verbose --default-exit-code 1

CMD ["snr"]
