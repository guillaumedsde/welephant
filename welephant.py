#!/usr/bin/env python
import argparse
import pathlib
import asyncio
import urllib.parse
import datetime

SUCCESS_RETURNCODE = 0


async def backup_database(backup_directory: pathlib.Path, database: str) -> None:
    parsed_db_uri = urllib.parse.urlparse(database)
    db_backup_date = datetime.date.today()
    backup_command = (
        "pg_dump",
        "--clean",
        "--if-exists",
        "--create",
        "--compress=zstd:11",
        f"--file={db_backup_date.isoformat()}_{parsed_db_uri.path}.sql.zst",
        database,
    )

    subprocess = await asyncio.create_subprocess_exec(*backup_command)

    stdout, stderr = await subprocess.communicate()

    if subprocess.returncode != SUCCESS_RETURNCODE:
        print(stderr)


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
