#!/usr/bin/env python

import argparse
import pathlib
import asyncio
import urllib.parse
import datetime


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


async def periodically_backup_databases(
    backup_interval: datetime.timedelta, backup_directory: pathlib.Path, *databases: str
) -> None:
    # TODO: signal handling
    while True:
        asyncio.create_task(backup_databases(backup_directory, *databases))
        await asyncio.sleep(backup_interval.total_seconds())


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
    parser.add_argument(
        "-i",
        "--backup-interval",
        type=int,
        help="Daily inteval at which to backup databases.",
        dest="backup_interval",
    )

    args = parser.parse_args()

    args.dumps_directory.mkdir(exist_ok=True)

    if args.backup_interval:
        await periodically_backup_databases(
            datetime.timedelta(days=args.backup_interval),
            args.dumps_directory,
            *args.database,
        )
    else:
        await backup_databases(args.dumps_directory, *args.database)


if __name__ == "__main__":
    asyncio.run(_main())
