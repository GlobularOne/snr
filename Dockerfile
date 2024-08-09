FROM ubuntu:22.04

RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    clang \
    curl \
    debootstrap \
    fakechroot \
    fakeroot \
    git \
    lld \
    make \
    nasm \
    python3 \
    && apt-get clean \
    &&  curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . /app

ENV POETRY_VIRTUALENVS_CREATE=false

RUN chmod +x ./tools/build_payloads.sh \
    && ./tools/build_payloads.sh && poetry install --only=main \
    && snr --init --init-only --verbose --default-exit-code 1

CMD ["snr"]
