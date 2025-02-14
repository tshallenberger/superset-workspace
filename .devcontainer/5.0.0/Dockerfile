# Apache Superset DevContainer v5.0.0
ARG VERSION=5.0.0rc1-py311
ARG BUILDPLATFORM=${BUILDPLATFORM:-linux/amd64}

# official registry/org
ARG DOCKER_REG=${DOCKER_REG:-docker.io}
ARG DOCKER_ORG=${DOCKER_ORG:-apache}

FROM --platform=${BUILDPLATFORM} ${DOCKER_REG}/${DOCKER_ORG}/superset:${VERSION}

ENV NODE_VERSION=20
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
  wget \
  zstd

RUN pip install --no-cache-dir --upgrade uv

# Using uv as it's faster/simpler than pip
RUN uv venv /workspace/.venv
ENV PATH="/workspace/.venv/bin:${PATH}"

USER $USER_NAME
ENV HOME=/home/$USER_NAME

# Install NVM, Node
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
# ENV NVM_DIR=/root/.nvm
ENV NVM_DIR=/home/$USER_NAME/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && \
  nvm use v${NODE_VERSION}



# Extension packages
# TODO: get this working in v5.0.0 with uv and venv

# RUN pip install authlib \
#   netaddr \
#   gevent \
#   statsd \
#   aiohttp \
#   jpype1 

# RUN pip install pyodbc \
#   mysqlclient \
#   mysql-connector-python \
#   pyhive \
#   sqlalchemy-drill \
#   redis \
#   sqlalchemy-vertica-python \
#   google

EXPOSE ${SUPERSET_PORT}
