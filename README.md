# Superset Workspace

A workspace for developing Apache Superset.

## Setup

Open workspace in VS Code, then select `Open in container`

Once the container is built, follow these steps to pull/build Superset:

```bash
# pull submodule
git submodule update --init
# PIP install superset
cd superset && pip install -e .
# NPM install
cd superset-frontend && npm ci && npm run build

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

# Run superset migrations, init roles, add admin user
superset db upgrade
superset init
superset fab create-admin \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname Admin \
    --email admin@superset.com
```

## Tools/Scripts

Display all networked containers (app, db, redis)

```bash

docker inspect superset_workspace_app-nw \
| jq '.[0].Containers[] 
| {Name, IPv4Address} 
| .["name"] = .Name
| .["ip"] = .IPv4Address 
| del(.Name, .IPv4Address)'

```

Check if db has migrations applied
Apply current migrations to db

## Scripts

```bash

superset db upgrade
superset init
superset fab create-admin \
  --username admin \
  --password admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@superset.com
              
```
