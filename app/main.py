import sys
import re
from datetime import datetime
import shutil
from pathlib import Path
import os
import logging
import uuid
import click
from .utils import getTimeData
from typing import List
import zipfile
import subprocess
import time

def setupLogger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)s | [%(uuid)s] | %(message)s',
        handlers=[
            logging.FileHandler("app.log"), # Save logs to a file
            logging.StreamHandler()          # Also print logs to the console
        ]
    )
    correlation_id = str(uuid.uuid4())[:8]
    return logging.LoggerAdapter(
        logging.getLogger(__name__), 
        {'uuid': correlation_id}
    )

def copyFile(original: Path) -> Path:
    newPath = original.with_stem(f"{original.stem}-revised")
    shutil.copy2(str(original), str(newPath))
    logger.debug(f"Wrote backup of {original} into {newPath}")
    return newPath

def patchDate(date: datetime, path: Path):
    try:
        # Equivalent to: sudo date -s "2025-12-27 14:30:00"
        data = path.read_bytes()
        commands = f"""
        rm -rf '{path}'
        sudo -v date -s '{date.strftime('%Y-%m-%d %H:%M:%S')}' && touch '{path}'
        """
        subprocess.run(commands, check=True, shell=True)
        path.write_bytes(data)
        timestamp = date.timestamp()
        os.utime(path, (timestamp, timestamp))
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run sudo: {e}")
        raise e
    finally:
        subprocess.run(["sudo", "hwclock", "-s"], check=True)

def patchDateWithBackup(date: datetime, path: Path):
    backup = path.parent / f"{path.name}.bak"
    try:
        shutil.copy2(path, backup)
        patchDate(date, path)
        backup.unlink()
    except Exception as e:
        shutil.copy2(backup, path)
        backup.unlink()
        raise e

def internalName(name: str):
    return name.startswith(".") or name.endswith(".log") or name.endswith(".bak")

def resolvePaths(paths: List[Path]) -> List[Path]:
    allPaths = set()
    for p in paths:
        absP = p.resolve()
        if internalName(absP.name):
            continue
        if absP.is_file():
                logger.info(f"Resolved file: {absP}")
                allPaths.add(absP)
        elif absP.is_dir():
            itr = absP.iterdir()
            allPaths.update(resolvePaths(list(itr)))
        else:
            info.warn(f"Unknown path type {absP}")
    return list(allPaths)

def extractDates(paths: List[Path]) -> List[tuple[datetime, Path]]:
    result = []
    for p in paths:
        date = getTimeData(p)
        if date is None:
            logger.warn(f"Failed to parse date of {p}. Will skip it!")
        else:
            logger.info(f"Parsed date of {p} is {date}")
            result.append((date, p))
    return result

def patchFiles(files: List[tuple[datetime, Path]]):
    for f in files:
        try:
            patchDateWithBackup(f[0], f[1])
        except Exception as e:
            logger.error(f"Failed to process {f[1]}: {e}")


@click.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True, path_type=Path))
def main(paths):
    """
    Changes the dates of images based on time metadata in their names

    paths: list of files or directories
    """
    global logger
    logger = setupLogger()

    allPaths = resolvePaths(paths)
    pathsWithDates = extractDates(allPaths)
    patchFiles(pathsWithDates)



if __name__ == '__main__':
    main()