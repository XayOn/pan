FROM python:3.10-slim
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime
RUN apt update && apt-get install --no-install-recommends -y curl build-essential pulseaudio-utils\
    && curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app
COPY . .
RUN pip install .
EXPOSE 8000
WORKDIR /app
CMD "/app/docker-entrypoint.sh"
