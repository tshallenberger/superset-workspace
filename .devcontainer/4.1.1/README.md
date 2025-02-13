# Superset 4.1.1 DevContainer

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
