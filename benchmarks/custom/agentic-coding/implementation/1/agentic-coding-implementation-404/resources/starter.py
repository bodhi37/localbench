"""Interval helpers for the scheduling pipeline (starter: implement me)."""


def merge_intervals(intervals):
    """Merge overlapping or touching intervals.

    Takes a list of 2-element [start, end] lists or tuples of ints with
    start <= end. Returns a NEW list of [start, end] lists sorted by start,
    merging every pair of overlapping or touching intervals (the next start
    is <= the current end). An empty input returns []. Does not modify the
    input.
    """
    raise NotImplementedError("implement me")


def is_covered(intervals, point):
    """Return True when some interval contains point (inclusive), else False."""
    raise NotImplementedError("implement me")
