#!/usr/bin/env python

import argparse
import asyncio
import datetime
import pathlib
from typing import Iterator
import urllib.parse
import sys
import os
import logging

_LOGGER = logging.getLogger(__name__)
_SUCCESS_RETURN_CODE = 0


async def backup_database(backup_directory: pathlib.Path, database: str) -> None:
    parsed_db_uri = urllib.parse.urlparse(database)

    db_name = parsed_db_uri.path.lstrip("/")

    backup_file_path = (
        backup_directory / f"{db_name}_{datetime.date.today().isoweekday()}.sql.zst"
    )
    backup_command = (
        "/usr/bin/env",
        "pg_dump",
        "--clean",
        "--if-exists",
        "--create",
        "--compress=zstd:11",
        f"--file={backup_file_path}",
        f"--dbname={database}",
    )

    _LOGGER.info(f"backing up {db_name} to {backup_file_path.absolute()}")

    process = await asyncio.create_subprocess_exec(
        *backup_command,
    )

    return_code = await process.wait()

    if return_code == _SUCCESS_RETURN_CODE:
        _LOGGER.info(f"Successfully backed up {db_name}")
    else:
        _LOGGER.error(f"Backup of {db_name} exited with return code {return_code}")


async def backup_databases(backup_directory: pathlib.Path, *databases: str) -> None:
    async with asyncio.TaskGroup() as tg:
        for database in databases:
            tg.create_task(backup_database(backup_directory, database))


def check_python_version() -> None:
    if not (sys.version_info.major >= 3 and sys.version_info.minor >= 11):
        raise RuntimeError("welephant requires python >= 3.11")


def database_uri_from_env() -> Iterator[str]:
    for key, value in os.environ.items():
        if key.startswith("WELEPHANT_URI_"):
            yield value


async def _main() -> None:
    check_python_version()

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="Welephant",
        description="CLI tool for periodically backing up mutliple PostgreSQL databases",
    )
    parser.add_argument(
        "database",
        type=str,
        nargs="*",
        default=set(database_uri_from_env()),
        help="PostgreSQL connection URI of database to backup.",
    )
    parser.add_argument(
        "-d",
        "--dumps-directory",
        type=pathlib.Path,
        default=pathlib.Path("./database_dumps"),
        help="Database backup destination directory",
        dest="dumps_directory",
    )

    args = parser.parse_args()

    # FIXME: better handling when no argument is given (our env var fallback is hacky)
    if len(args.database) == 0:
        parser.print_help()
        sys.exit(0)

    _LOGGER.info(f"Starting backup of {len(args.database)} database(s)")

    args.dumps_directory.mkdir(exist_ok=True)

    await backup_databases(args.dumps_directory, *args.database)

    _LOGGER.info("Finished backups")


if __name__ == "__main__":
    asyncio.run(_main())
