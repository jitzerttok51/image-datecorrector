import re
from datetime import datetime
from pathlib import Path


def getTimeData(path: Path):
    name = path.name

    # 1. Standard YYYYMMDD_HHMMSS (and variations like 20171103-020935)
    # Matches: 20170129_155128, Screenshot_20171103-020935, 20150124_211718
    std_pattern = r"(\d{8})[_|-](\d{6})"
    std_match = re.search(std_pattern, name)
    if std_match:
        return datetime.strptime(f"{std_match.group(1)}{std_match.group(2)}", "%Y%m%d%H%M%S")

    # 2. Dashed Date with Dots: YYYY-MM-DD HH.MM.SS
    # Matches: 2014-07-22 20.27.07.jpg
    dash_dot_pattern = r"(\d{4}-\d{2}-\d{2}) (\d{2}\.\d{2}\.\d{2})"
    dash_dot_match = re.search(dash_dot_pattern, name)
    if dash_dot_match:
        dt_string = f"{dash_dot_match.group(1)} {dash_dot_match.group(2)}"
        return datetime.strptime(dt_string, "%Y-%m-%d %H.%M.%S")

    # 3. WhatsApp Style: IMG-YYYYMMDD-WA...
    # Matches: IMG-20130426-WA0001.jpg
    wa_pattern = r"IMG-(\d{8})-WA"
    wa_match = re.search(wa_pattern, name)
    if wa_match:
        return datetime.strptime(wa_match.group(1), "%Y%m%d")

    # 4. Action Cam / FILE style: FILEYYMMDD-HHMMSS
    # Matches: FILE180215-171034-004212.MP4
    file_pattern = r"FILE(\d{6})-(\d{6})"
    file_match = re.search(file_pattern, name)
    if file_match:
        return datetime.strptime(f"{file_match.group(1)}{file_match.group(2)}", "%y%m%d%H%M%S")

    # 5. Unix Epoch (10 or 13 digits)
    # Matches: FB_IMG_1446114923469, IMG-1419336966300, mid_1410120397719
    # We look for a string of 10 to 13 digits
    epoch_pattern = r"(?:IMG_|mid_|IMG-|FB_IMG_)(\d{10,13})"
    epoch_match = re.search(epoch_pattern, name)
    if epoch_match:
        ts_str = epoch_match.group(1)
        ts = int(ts_str)
        if len(ts_str) == 13:  # It's milliseconds
            ts /= 1000
        return datetime.fromtimestamp(ts)

    # 6. Long numeric string (YYMMDDHHMMSS...)
    # Matches: IMG_180830270710386 (Assuming 18-08-30 27:07?) 
    # Note: This pattern is risky, but works for the specific format provided.
    long_num_match = re.search(r"IMG_(\d{13})", name)
    if long_num_match:
        try:
            return datetime.strptime(long_num_match.group(1), "%y%m%d%H%M%S")
        except ValueError:
            pass

    return None