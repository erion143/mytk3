def parser(source, format_args,
           encoding='utf-8', separator='\t',
           filt=(lambda x: True),
           replacement=None,
           source_is_file=True,
           loglevel='INFO'):
    if replacement is None:
        replacement = []
    if source_is_file:
        if loglevel == 'INFO':
            print(source)
        with open(source, 'r', encoding=encoding) as fn:
            data = fn.readlines()
    else:
        data = source

    result = [[] for i in format_args]

    for line in data:
        if loglevel == 'DEBUG':
            print(line.strip(), filt(line))
        if not filt(line):
            continue
        line_ = line # Дабы не изменять исзодные строки
                     # если источник - массив, а не файл
        for src, tgt in replacement:
            if src in line:
                if loglevel == 'DEBUG':
                    print("Replace {} in {}".format(src, line))
                line_ = line_.replace(src, tgt)
        if loglevel == 'DEBUG':
            print(line_)
        try:
            new_line = split_line(line_.strip(), format_args, separator)
        except ValueError:
            print('ValueError')
            continue
        except AssertionError:
            print('AssertionError')
            continue
        else:
            for mass, val in zip(result, new_line):
                mass.append(val)

    return result


def split_line(line, format_args, separator):
    new_line = line.split(separator)
    assert len(new_line) == len(format_args)
    array = zip(new_line, format_args)
    return [f(i) for (i, f) in array]
