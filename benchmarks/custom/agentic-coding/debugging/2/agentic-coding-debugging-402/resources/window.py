"""Sliding-window helpers for the yard telemetry pipeline.

This module is used by downstream reporting code. The three public functions
below are expected to follow their docstrings exactly.
"""


def max_window_sums(values, k):
    """Return the largest sum over every contiguous window of exactly k
    elements of values, or None when k <= 0 or k > len(values).
    Must not modify values.
    """
    if k <= 0 or k > len(values):
        return None
    best = 0
    for i in range(len(values) - k):
        total = sum(values[i:i + k])
        if total > best:
            best = total
    return best


def count_windows_over(values, k, threshold):
    """Return how many contiguous windows of exactly k elements of values have
    a sum STRICTLY greater than threshold, or None when k <= 0 or
    k > len(values). Must not modify values.
    """
    if k <= 0 or k > len(values):
        return None
    count = 0
    for i in range(len(values) - k):
        if sum(values[i:i + k]) > threshold:
            count += 1
    return count


def window_starts(values, k):
    """Return the starting indices of all contiguous windows of exactly k
    elements of values, in increasing order, or [] when k <= 0 or
    k > len(values). Must not modify values.
    """
    if k <= 0 or k > len(values):
        return []
    return list(range(len(values) - k + 1))
