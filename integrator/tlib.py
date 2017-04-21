def make_weight(source, *rules):
    start = 1
    current = 0
    res = []

    for i in source:
        if current >= len(rules):
            res.append(start)
        elif i < rules[current][0]:
            res.append(start)
        else:
            start = rules[current][1]
            current += 1
            res.append(start)

    return res


def integrator(xs, ys, x_min=None, x_max=None):
    # Это писец, товарици. Как бы сделать по красивее?
    if x_min is not None:
        foo = [x >= x_min for x in xs]
    else:
        foo = []
    if x_max is not None:
        bar = [x <= x_max for x in xs]
    else:
        bar = []
    if foo and bar:
        res = [lx and rx for lx, rx in zip(foo, bar)]
        xs = [x for x, lx in zip(xs, res) if lx]
        ys = [y for y, lx in zip(ys, res) if lx]
    elif foo:
        xs = [x for x, lx in zip(xs, foo) if lx]
        ys = [y for y, lx in zip(ys, foo) if lx]
    elif bar:
        xs = [x for x, lx in zip(xs, bar) if lx]
        ys = [y for y, lx in zip(ys, bar) if lx]

    summ = 0
    for (x1, y1), (x2, y2) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        summ += ((y1 + y2) / 2 * (x2 - x1))

    return summ


def intervals(xs):
    for x1, x2 in zip(xs, xs[1:]):
        yield x2 - x1


def speed(ts, vs):
    volumes = []
    speeds = []

    for v, dt, dv in zip(vs, intervals(ts), intervals(vs)):
        volumes.append(v + dv // 2)
        speeds.append(round(dv / dt, 2))

    return volumes, speeds


