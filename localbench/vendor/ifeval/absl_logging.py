"""Minimal stand-in for `absl.logging`.

The vendored IFEval grader only ever calls `logging.error(...)`. Keeping this
shim local avoids pulling the `absl-py` distribution in for one call site.
"""
from __future__ import annotations

import logging as _logging

_log = _logging.getLogger("localbench.ifeval")


def error(msg, *args, **kwargs):  # noqa: A001 - mirrors absl's API
    _log.error(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):  # noqa: A001
    _log.warning(msg, *args, **kwargs)


def info(msg, *args, **kwargs):  # noqa: A001
    _log.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):  # noqa: A001
    _log.debug(msg, *args, **kwargs)
