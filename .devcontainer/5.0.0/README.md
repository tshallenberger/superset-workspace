# Superset 5.0.0 DevContainer

## Pre-init

Before opening the devcontainer, your Rancher Desktop preferences should be:

```bash
- Should be run with admin access
- Virtual Machine > Hardware > Memory # Greater than 16, preferably 20+ GB
- Virtual Machine > Hardware > CPUs   # Greater than 16, preferably 20+ GB
- Virtual Machine > Volumes > Mount Type # virtiofs (uses Apple Virtualization)
- Virtual Machine > Emulation > Virtual Machine Type # VZ
- Kubernetes # Disable Kubernetes, Disable Traefik

```

## MySQL (Superset DB)

When booting up the container, you should be able to access an empty MySQL container with the following credentials:

```bash
mysql -usuperset -psuperset -h db

MySQL [(none)]> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| superset           |
| sys                |
+--------------------+

```

## Setup

```bash
source .venv/bin/activate
uv pip install -e superset/
uv pip install mysql-connector-python authlib
superset db upgrade
superset init
superset fab create-admin \
  --username admin \
  --firstname Superset \
  --lastname Admin \
  --email admin@superset.com \
  --password admin
superset load-examples
```
