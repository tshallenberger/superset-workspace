# Superset Workspace

A workspace for developing a separate fork of Apache Superset.

## Bugs

`superset-frontend` won't build with following enabled in Docker on a Macbook M3:

`Rosetta for x86/amd64 emulation on Apple Silicon`

## Setup

Open workspace in VS Code, then select `Dev Containers: Rebuild and Reopen in container`

This should spin up a docker-compose project called `superset_workspace` with child containers: `app`, `db` `redis`

Once the container is built, follow these steps to pull/build Superset:

```bash
# pull submodule
git submodule update --init
# PIP install superset
uv venv .venv
source .venv/bin/activate
uv pip install -e superset/
uv pip install mysql-connector-python authlib
# NPM install
cd /workspace/superset/superset-frontend && npm ci && npm run build

# Drop/Rebuild Superset Database
mysql -h db \
-psuperset \
-e "
DROP USER IF EXISTS superset@'%';
DROP USER IF EXISTS superset@localhost;
DROP DATABASE IF EXISTS superset;
CREATE DATABASE IF NOT EXISTS superset;
CREATE USER superset@'%' IDENTIFIED BY 'superset';
CREATE USER superset@localhost IDENTIFIED BY 'superset';
GRANT ALL PRIVILEGES ON *.* TO superset@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO superset@localhost WITH GRANT OPTION;
"

# Run superset migrations, init roles, add admin user, load examples
superset db upgrade
superset init
superset fab create-admin \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname Admin \
  --email admin@superset.com
superset load_examples --force
```

## Tools/Scripts

Display all networked containers (app, db, redis)

```bash

docker inspect superset_network \
| jq '.[0].Containers[] 
| {Name, IPv4Address} 
| .["name"] = .Name
| .["ip"] = .IPv4Address 
| del(.Name, .IPv4Address)'

```

## Init venv
