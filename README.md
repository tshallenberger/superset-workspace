# Superset Workspace

A workspace for developing Apache Superset.

## Init

1. Add superset as submodule
2. Add a vscode devcontainer for latest release branch
   1. Dockerfile: based from official apache/superset image, extended with dev and debug tooling
   2. docker-compose.yml
      1. network:
         1. superset_workspace_app-nw
   3. devcontainer.json
   4. .vscode: launch.json

## Goals

1. Launch a workspace for Apache Superset using a container that extends the official image
2. Workspace should launch with ability to run Superset with debug enabled
3. Workspace should launch with ability to run Superset with SSL enabled (TLS)
4. Workspace should launch with ability to build Superset UI (node/npm)
5. Workspace should launch with a local MySQL container as a metastore
6. Workspace should launch with ability to run migrations against local db container
7. Workspace should launch with a local Redis container for caching
8. Workspace should launch with an extensions volume mounted and config file loaded at runtime (superset_config.py)

## Acceptance Criteria

1. User should be able to:
   1. Clone workspace repo
   2. Open in VS Code
   3. Open in container
   4. Pip install requirements
   5. Install npm packages
   6. Build superset-frontend
   7. Build Superset Docker image
   8. Launch Superset with debugging/SSL enabled
   9. Launch Superset with a custom superset_config.py file
   10. Query a local db container
   11. Connect to the workspace db container with a tool like Datagrip
   12. Connect to the workspace redis container with a tool like Redis Commander

## Scripts

```bash

docker inspect superset_workspace_app-nw \
| jq '.[0].Containers[] 
| {Name, IPv4Address} 
| .["name"] = .Name
| .["ip"] = .IPv4Address 
| del(.Name, .IPv4Address)'

superset db upgrade
superset fab create-admin \
              --username admin \
              --password admin \
              --firstname Superset \
              --lastname Admin \
              --email admin@superset.com
              
```
