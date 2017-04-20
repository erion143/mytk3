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
