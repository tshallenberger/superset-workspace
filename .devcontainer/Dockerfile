# Apache Superset DevContainer


ARG SUPERSET_VER=4.0.0-dev
ARG SUPERSET_PORT=${SUPERSET_PORT:-8088}
ARG BUILDPLATFORM=${BUILDPLATFORM:-linux/amd64}
ARG DOCKER_ORG=${DOCKER_ORG:-apache}

FROM --platform=${BUILDPLATFORM} ${DOCKER_ORG}/superset:${SUPERSET_VER}

ARG USERNAME

USER root

RUN useradd --uid 501 --gid 20 -m --no-log-init --shell /bin/bash $USERNAME \
  && apt-get update \
  && apt-get install -y sudo \
  && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
  && chmod 0440 /etc/sudoers.d/$USERNAME

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

USER $USERNAME
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
  sqlalchemy-vertica-python

EXPOSE ${SUPERSET_PORT}
