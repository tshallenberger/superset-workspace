#!/bin/bash
# Get the current user's UID, GID 
USER_UID=$(id -u)
USER_GID=$(id -g)

# Write the environment variables to the .env file
echo "USER_UID=$USER_UID" > .devcontainer/.env
echo "USER_GID=$USER_GID" >> .devcontainer/.env
echo "USER=$USER" >> .devcontainer/.env
echo "TLS=$HOME/.tls" >> .devcontainer/.env
echo "CERTS=$HOME/.certs" >> .devcontainer/.env
echo "MYSQL_DATA=./volumes/mysql/data" >> .devcontainer/.env
echo "MYSQL_INI=./volumes/mysql/ini/0_init.sql" >> .devcontainer/.env
echo "MYSQL_ROOT_PASSWORD=superset" >> .devcontainer/.env
echo "MYSQL_USER=superset" >> .devcontainer/.env
echo "MYSQL_PASSWORD=superset" >> .devcontainer/.env
echo "MYSQL_DATABASE=superset" >> .devcontainer/.env
echo ".env file generated!"