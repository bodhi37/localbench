#!/bin/sh
# Teardown for cybersecurity-ctf-502.
# The task runs no service; remove interpreter caches if any were created.
find "$(dirname "$0")" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
exit 0