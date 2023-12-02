ARG BUILDPLATFORM=${BUILDPLATFORM:-linux/amd64}
ARG SUPERSET_VER=3.0.2

FROM --platform=linux/amd64 apache/superset:${SUPERSET_VER}-dev

USER root

ENV NODE_VERSION=16 

RUN apt update && \
    apt install -y \
    default-mysql-client \
    gdb \
    net-tools

RUN apt-get update -q \
    && apt-get install -yq \
    iputils-ping \
    gdb \
    curl \
    git \
    ssh \
    vim \
    zsh \
    nmap \
    jq 

# Install Docker CE CLI
RUN apt-get update \
    && apt-get install -y apt-transport-https ca-certificates curl gnupg2 lsb-release \
    && curl -fsSL https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]')/gpg | apt-key add - 2>/dev/null \
    && echo "deb [arch=amd64] https://download.docker.com/linux/$(lsb_release -is | tr '[:upper:]' '[:lower:]') $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli

RUN pip install --upgrade pip
# Install python formatter
RUN pip install black
# RUN pip install authlib \
#     netaddr \
#     gevent \
#     statsd \
#     aiohttp \
#     jpype1 \
#     black

RUN pip install mysql-connector-python
#     pyhive \
#     sqlalchemy-drill \
#     pyodbc \
#     redis

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && \
    nvm use v${NODE_VERSION} && \
    npm i -g yarn pnpm

USER root

EXPOSE ${SUPERSET_PORT}
