#!/bin/bash

function revise {
    FILE=$1
    # Regex pattern to match YYYYMMDD and HHMMSS separated by an underscore
    # It captures the date in group 1 and time in group 2
    PATTERN="([0-9]{8})_([0-9]{6})"

    if [[ $FILE =~ $PATTERN ]]; then
        DATE_PART="${BASH_REMATCH[1]}"
        TIME_PART="${BASH_REMATCH[2]}"

        local EXIF_TIME="${DATE_PART:0:4}-${DATE_PART:4:2}-${DATE_PART:6:2} ${TIME_PART:0:2}:${TIME_PART:2:2}:${TIME_PART:4:2}"
        TOUCH_FORMAT="${DATE_PART}${TIME_PART:0:4}.${TIME_PART:4:2}"
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
    fi
}

revise $1
