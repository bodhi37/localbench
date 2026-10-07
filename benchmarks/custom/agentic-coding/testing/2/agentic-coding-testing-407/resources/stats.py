"""Summary statistics for the telemetry pipeline (BUGGY: fix me)."""


def mean(xs):
    """Return sum(xs)/len(xs) as a float, or None when xs is empty."""
    if len(xs) == 0:
        return None
    total = xs[0]
    for x in xs:
        total += x
    return total / len(xs)


def median(xs):
    """Return the middle value (odd length) or the mean of the two middle
    values (even length) of a sorted copy of xs, or None when empty."""
    if len(xs) == 0:
        return None
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid] + s[mid + 1]) / 2


def mode(xs):
    """Return the most frequent value (ties go to the smallest), or None."""
    if len(xs) == 0:
        return None
    xs.sort()
    best, best_count = xs[0], 1
    cur, cur_count = xs[0], 1
    for x in xs[1:]:
        if x == cur:
            cur_count += 1
        else:
            if cur_count > best_count:
                best, best_count = cur, cur_count
            cur, cur_count = x, 1
    if cur_count > best_count:
        best = cur
    return best
