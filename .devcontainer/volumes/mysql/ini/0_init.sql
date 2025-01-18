CREATE DATABASE IF NOT EXISTS superset;
DROP USER IF EXISTS superset@'%';
DROP USER IF EXISTS superset@localhost;
CREATE USER superset@'%' IDENTIFIED BY 'superset';
CREATE USER superset@localhost IDENTIFIED BY 'superset';
GRANT ALL PRIVILEGES ON *.* TO superset@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO superset@localhost WITH GRANT OPTION;