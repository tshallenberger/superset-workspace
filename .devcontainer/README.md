# superset-devcontainer

A devcontainer setup for developing Apache Superset.

## Bugs

superset-frontend won't build on `Rosetta for x86/amd64 emulation on Apple Silicon`

## Helpers

```bash


# Show current migration
mysql -h db \
-usuperset \
-psuperset \
superset \
-e "SELECT version_num FROM alembic_version;"

# f3c2d8ec8595 - 2.1.0
# 4b85906e5b91 - 3.0.1

# Show table schema, name, size
mysql -h db \
-psuperset \
-e "
SELECT
table_schema as \`Database\`,
table_name AS \`Table\`,
round(((data_length + index_length) / 1024 / 1024), 2) \`Size in MB\`
FROM information_schema.TABLES
WHERE table_schema = 'superset'
ORDER BY (data_length + index_length) DESC;
"

# Show superset tables, row count
mysql -h db \
-psuperset \
-e "
SELECT table_name AS 'table',
table_rows AS 'rows'
FROM information_schema.tables
WHERE table_schema = 'superset'
ORDER BY table_rows ASC
"

# Show schemas
mysql -h db \
-usuperset \
-psuperset \
-e "
SELECT SCHEMA_NAME
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE SCHEMA_NAME='superset';
"

# Show users
mysql -h db \
-psuperset \
-e "
SELECT host, user FROM mysql.user ORDER BY user;
"

# Reset Superset DB User
mysql -h db \
-psuperset \
-e "
DROP USER IF EXISTS superset@'%';
DROP USER IF EXISTS superset@localhost;
CREATE USER superset@'%' IDENTIFIED BY 'superset';
CREATE USER superset@localhost IDENTIFIED BY 'superset';
GRANT ALL PRIVILEGES ON *.* TO superset@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON *.* TO superset@localhost WITH GRANT OPTION;
"


# test connection:
until mysql -h db \
  -psuperset \
  -e "SHOW DATABASES;"; do
    if (( attempt_num == max_attempts ))
    then
        echo "Attempt $attempt_num failed and there are no more attempts left!"
        return 1
    else
        echo "Attempt $attempt_num failed! Trying again in $attempt_num seconds..."
        sleep $(( attempt_num++ ))
    fi
done

```
