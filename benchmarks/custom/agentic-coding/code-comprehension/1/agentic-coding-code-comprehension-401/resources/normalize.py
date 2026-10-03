def stable_buckets(values, width):
    buckets = {}
    for v in values:
        key = int(v / width)
        buckets.setdefault(key, []).append(v)
    return buckets


def summarize(values, width=10):
    out = []
    for key, members in sorted(stable_buckets(values, width).items()):
        out.append(f"{key}:{len(members)}")
    return ",".join(out)


if __name__ == "__main__":
    print(summarize([3, 11, 19, 20, -1, 0]))
