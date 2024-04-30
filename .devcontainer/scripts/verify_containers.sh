#!/usr/bin/bash

# Ouput all containers (and their IPv4 address) in workspace
docker inspect superset_network \
| jq '.[0].Containers[]
| {Name, IPv4Address}
| .["name"] = .Name
| .["ip"] = .IPv4Address
| del(.Name, .IPv4Address)'