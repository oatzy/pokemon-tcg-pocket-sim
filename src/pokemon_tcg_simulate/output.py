def avg(counter):
    if el := list(counter.elements()):
        return sum(el) / len(el)
    return None


def percentiles(counter, total):
    points = [i * total for i in (0.5, 0.75, 0.9, 0.95)]
    results = []
    values = sorted(counter.items())

    offset = 0
    s = 0
    i = 0
    while offset < len(points) and i < len(values):
        if s >= points[offset]:
            results.append(values[i][0])
            offset += 1
        else:
            s += values[i][1]
            i += 1
    return results


def dump_histograms(histograms, file=None):
    upper = max(max(h.keys()) for h in histograms.values())
    keys = list(histograms)

    print(",".join(["opened", *keys]), file=file)
    for i in range(upper + 1):
        print(
            ",".join(map(str, [i] + [histograms[k].get(i, 0) for k in keys])), file=file
        )
