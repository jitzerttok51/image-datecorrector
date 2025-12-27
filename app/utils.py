import re
from datetime import datetime
from pathlib import Path


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