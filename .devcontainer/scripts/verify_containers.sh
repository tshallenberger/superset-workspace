#!/usr/bin/bash

echo "######### CONTAINERS #########"
# Ouput all containers in workspace
docker inspect superset_workspace_app-nw \
| jq '.[0].Containers[] 
| {Name, IPv4Address} 
| .["name"] = .Name
| .["ip"] = .IPv4Address 
| del(.Name, .IPv4Address)'