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

def zipPaths(paths: List[Path]):
    """
    Zips a list of Path objects into a single archive.
    """
    with zipfile.ZipFile("archive.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for path in paths:
            if path.exists():
                # arcname determines the name of the file inside the zip
                # path.name ensures it doesn't store the full absolute path
                zipf.write(path, arcname=path.name)
            else:
                logger.warn(f"Warning: {path} does not exist, skipping.")

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

def setModificationDate(path: Path, date):
    timestamp = date.timestamp()
    os.utime(str(path), (timestamp, timestamp))

def getTimeData(path: Path):
    """
    Analyzes filename for YYYYMMDD_HHMMSS or Unix Epoch patterns.
    Returns a single datetime object or None if no match found.
    """
    # Pattern 1: 20231025_123045
    std_pattern = r"([0-9]{8})_([0-9]{6})"
    # Pattern 2: mid_1410120397719 (extracting the 10-digit seconds part)
    epoch_pattern = r"mid_([0-9]{10})"

    # Check for Standard YYYYMMDD_HHMMSS
    std_match = re.search(std_pattern, path.name)
    if std_match:
        dt_string = std_match.group(1) + std_match.group(2)
        return datetime.strptime(dt_string, "%Y%m%d%H%M%S")

    # Check for Epoch (received_m_mid_...)
    epoch_match = re.search(epoch_pattern, path.name)
    if epoch_match:
        seconds = int(epoch_match.group(1))
        return datetime.fromtimestamp(seconds)

    return None

def unzipWithCorrectDate(date: datetime, path: Path):
    try:
        # Equivalent to: sudo date -s "2025-12-27 14:30:00"
        subprocess.run(["sudo", "date", "-s", date.strftime('%Y-%m-%d %H:%M:%S')], check=True)
        subprocess.run(["rm", "-rf", path.name], check=True)
        subprocess.run(["unzip", "-j", "archive.zip", path.name], check=True)
        os.chmod(str(path), 0o644)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to run sudo: {e}")
    finally:
        subprocess.run(["sudo", "hwclock", "-s"], check=True)

@click.command()
@click.argument('filename')
def main(filename):
    """
    Metadata Revision Tool.

    FILENAME: The path to the image file you want to process.
    """
    global logger
    logger = setupLogger()
    inputFile = Path(filename)
    date = getTimeData(inputFile)
    if date is None:
        logger.warn(f"Failed to parse date of {inputFile}. Will skip it!")
        return None
    else:
        logger.info(f"Parsed date of {inputFile} is {date}")
    copy = copyFile(Path(sys.argv[1]))
    setModificationDate(copy, date)
    Path("archive.zip").unlink(missing_ok=True)
    zipPaths([copy])
    unzipWithCorrectDate(date, copy)
    Path("archive.zip").unlink(missing_ok=True)


if __name__ == '__main__':
    main()