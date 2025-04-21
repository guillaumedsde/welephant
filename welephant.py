#!/usr/bin/env python

import argparse
import asyncio
import datetime
import pathlib
import urllib.parse


async def backup_database(backup_directory: pathlib.Path, database: str) -> None:
    parsed_db_uri = urllib.parse.urlparse(database)

    backup_file_path = (
        backup_directory
        / f"{parsed_db_uri.path.lstrip('/')}_{datetime.date.today().isoweekday()}.sql.zst"
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

    print(f"backing up {database} to {backup_file_path}")

    process = await asyncio.create_subprocess_exec(
        *backup_command,
    )

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
    parser.add_argument(
        "database",
        type=str,
        nargs="+",
        help="PostgreSQL connection URI of databasae to backup.",
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

    args.dumps_directory.mkdir(exist_ok=True)

    await backup_databases(args.dumps_directory, *args.database)


if __name__ == "__main__":
    asyncio.run(_main())
