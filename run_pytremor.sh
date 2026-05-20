#!/bin/bash
LOCKFILE=/tmp/pytremor.lock

# Exit if another instance is already running
if [ -f "$LOCKFILE" ] && kill -0 "$(cat $LOCKFILE)" 2>/dev/null; then
    echo "$(date): pyTREMOR already running (PID $(cat $LOCKFILE)), skipping." >> /Users/sjc/pytremor/logs/cron.log
    exit 1
fi

echo $$ > "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

cd /Users/sjc/pytremor
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 pyTREMOR.py --autorun >> /Users/sjc/pytremor/logs/cron.log 2>&1
