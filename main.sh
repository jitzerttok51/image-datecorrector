#!/bin/bash

function revise {
    FILE=$1
    # Regex pattern to match YYYYMMDD and HHMMSS separated by an underscore
    # It captures the date in group 1 and time in group 2
    PATTERN="([0-9]{8})_([0-9]{6})"
    # Pattern 2: Unix Timestamp (milliseconds) - look for 'mid_' followed by digits
    local epoch_pattern="mid_([0-9]{10})[0-9]{3}"

    local EXIF_TIME=""
    local TOUCH_FORMAT=""

    if [[ $FILE =~ $PATTERN ]]; then
        local DATE_PART="${BASH_REMATCH[1]}"
        local TIME_PART="${BASH_REMATCH[2]}"
        EXIF_TIME="${DATE_PART:0:4}-${DATE_PART:4:2}-${DATE_PART:6:2} ${TIME_PART:0:2}:${TIME_PART:2:2}:${TIME_PART:4:2}"
        TOUCH_FORMAT="${DATE_PART}${TIME_PART:0:4}.${TIME_PART:4:2}"
    elif [[ $input_str =~ $epoch_pattern ]]; then
        local epoch_seconds="${BASH_REMATCH[1]}"
        EXIF_TIME=$(date -d "@$epoch_seconds" "+%Y-%m-%d %H:%M:%S")
        TOUCH_FORMAT=$(date -d "@$epoch_seconds" "+%Y%m%d%H%M.%S")
    fi

    FILENAME="${FILE%.*}"
    EXTENSION="${FILE##*.}"
    NEW_NAME="${FILENAME}-revised.${EXTENSION}"

    cp "$FILE" "$NEW_NAME"
    touch -m -a -t "$TOUCH_FORMAT" "$NEW_NAME"
    zip -X archive.zip "$NEW_NAME"
    rm "$NEW_NAME"
    echo "$EXIF_TIME"
    sudo date -s "$EXIF_TIME"
    unzip archive.zip
    chmod 644 "$NEW_NAME"
    sudo hwclock -s
    rm -rf archive.zip
}

revise $1
