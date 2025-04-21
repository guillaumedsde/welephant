#!/usr/bin/env python

import argparse
import pathlib
import asyncio
import urllib.parse
import datetime


async def backup_database(backup_directory: pathlib.Path, database: str) -> None:
    parsed_db_uri = urllib.parse.urlparse(database)
    db_backup_date = datetime.date.today()

    backup_file_path = (
        backup_directory
        / f"{db_backup_date.isoformat()}_{parsed_db_uri.path.lstrip('/')}.sql.zst"
    )
    backup_command = (
        "/usr/bin/env",
        "pg_dump",
        "--clean",
        "--if-exists",
        "--create",
        "--compress=zstd:11",
        f"--file={backup_file_path}",
        database,
    )

    process = await asyncio.create_subprocess_exec(*backup_command)

    await process.wait()


async def backup_databases(backup_directory: pathlib.Path, *databases: str) -> None:
    async with asyncio.TaskGroup() as tg:
        for database in databases:
            tg.create_task(backup_database(backup_directory, database))


async def _main() -> None:
    parser = argparse.ArgumentParser(
        prog="Welephant",
        description="CLI tool for periodically backing up mutliple PostgreSQL databases",
    )
    parser.add_argument("database", type=str, nargs="+")
    parser.add_argument(
        "-d",
        "--dumps-directory",
        type=pathlib.Path,
        default=pathlib.Path("./database_dumps"),
        dest="dumps_directory",
    )

    args = parser.parse_args()

    args.dumps_directory.mkdir(exist_ok=True)

    await backup_databases(args.dumps_directory, *args.database)


if __name__ == "__main__":
    asyncio.run(_main())
