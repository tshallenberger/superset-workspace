# Apache Superset DevContainer v4.1.1
ARG VERSION=4.1.1-dev
ARG BUILDPLATFORM=${BUILDPLATFORM:-linux/amd64}

# official registry/org
ARG DOCKER_REG=${DOCKER_REG:-docker.io}
ARG DOCKER_ORG=${DOCKER_ORG:-apache}

FROM --platform=${BUILDPLATFORM} ${DOCKER_REG}/${DOCKER_ORG}/superset:${VERSION}

ENV NODE_VERSION=18
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ARG SUPERSET_PORT=${SUPERSET_PORT:-8088}

ARG USER_NAME
ARG USER_UID
ARG USER_GID

USER root

RUN useradd --uid $USER_UID --gid $USER_GID -m --no-log-init --shell /bin/bash $USER_NAME \
  && apt-get update \
  && apt-get install -y sudo \
  && echo $USER_NAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER_NAME \
  && chmod 0440 /etc/sudoers.d/$USER_NAME

# Troubleshooting tools
RUN apt update && \
  apt install -y \
  default-mysql-client \
  net-tools \
  less

# Container tools
RUN apt-get update -q \
  && apt-get install -yq --no-install-recommends \
  make \
  g++ \
  unixodbc \
  unixodbc-dev \
  build-essential \
  libsasl2-dev \
  libsasl2-modules-gssapi-mit \
  libpq-dev \
  libecpg-dev \
  libldap2-dev \
  git \
  ssh \
  netcat-traditional \
  curl \
  iputils-ping \
  jq \
  wget

# Extension packages
RUN pip install authlib \
  netaddr \
  gevent \
  statsd \
  aiohttp \
  jpype1 

RUN pip install pyodbc \
  mysqlclient \
  mysql-connector-python \
  pyhive \
  sqlalchemy-drill \
  redis \
  sqlalchemy-vertica-python \
  google

USER ${USER_NAME}

# Install nvm/node 
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
# ENV NVM_DIR=/root/.nvm
ENV NVM_DIR=/home/$USER_NAME/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && \
  nvm use v${NODE_VERSION}

EXPOSE ${SUPERSET_PORT}
