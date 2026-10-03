"""Vendored copy of Google Research's IFEval instruction checkers.

Upstream: https://github.com/google-research/google-research/tree/master/instruction_following_eval
Licence:  Apache License 2.0 (see NOTICE)

Modifications from upstream, nothing else:
  * package-relative imports (``from . import ...``)
  * ``from absl import logging`` replaced by the local ``absl_logging`` shim,
    so grading does not require the ``absl-py`` distribution

The 25 instruction checkers and the instruction-id registry are verbatim, so
scores stay comparable with published IFEval results.
"""
from .instructions_registry import INSTRUCTION_CONFLICTS, INSTRUCTION_DICT  # noqa: F401

__all__ = ["INSTRUCTION_DICT", "INSTRUCTION_CONFLICTS"]
