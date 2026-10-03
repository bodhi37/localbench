#!/bin/sh
# Teardown for cybersecurity-offsec-503.
# The task starts a loopback-only service; make sure nothing survives the run.
TASK_DIR=$(cd "$(dirname "$0")" && pwd)
# kill only our relay process, matched by its full path, never a blanket pattern
pkill -f "[r]elay.py --port" 2>/dev/null || true
pkill -f "[r]elay.py$" 2>/dev/null || true
find "$TASK_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
exit 0