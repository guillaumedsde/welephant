# 🐘 Welephant

Welephant is a small CLI to help asynchronously dump PostgreSQL databases to a local directory using `pg_dump`.

## 🏁 Usage

```
$ ./welephant.py --help                                                                                           git_repositories/welephant
usage: Welephant [-h] [-d DUMPS_DIRECTORY] database [database ...]

CLI tool for periodically backing up mutliple PostgreSQL databases

positional arguments:
  database              PostgreSQL connection URI of databasae to backup.

options:
  -h, --help            show this help message and exit
  -d, --dumps-directory DUMPS_DIRECTORY
                        Database backup destination directory
```

## 🐋 Docker image

Welephant can also be run with a docker image

```bash
docker build --tag welephant .
# Run a "one shot" database backup
docker run welephant postgres://postgres:postgres@postgres:5432/postgres
# Schedule backups with supercronic
cat <<EOF ./crontab
5 4 * * * /welephant postgres://postgres:postgres@postgres:5432/postgres
EOF
docker run \
    --entrypoint /usr/bin/supercronic \
    --volume ./crontab:/data/crontab:ro \
    welephant
```

## 🛠️ Local development

Welephant is written to work on Python 3.11 or greater using only the standard library.

A [`compose.yml`](./compose.yml) file is available for testing the project.
