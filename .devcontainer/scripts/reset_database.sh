#!/usr/bin/bash

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