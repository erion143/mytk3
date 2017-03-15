def next_letter(letter):
    if ord(letter) >= 90:
        raise ValueError('Only for upper ascii')
    return chr(ord(letter) + 1)


def write_to_xls(book, sheet, *data, line=1, start_column='A'):
    columns = [start_column]
    if len(data) > 1:
        for i in range(len(data) - 1):
            columns.append(next_letter(columns[-1]))

    if sheet not in book.sheetnames:
        ws = book.create_sheet(title=sheet)
    else:
        ws = book.get_sheet_by_name(sheet)
    print(book.sheetnames)
    print(type(ws))
    for i in range(len(data[0])):
        for col, val in zip(columns, data):
            cell = '{}{}'.format(col, line)
            ws[cell] = val[i]
        line += 1
