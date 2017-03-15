from tkinter.messagebox import askyesno
from tkinter.simpledialog import askstring


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


def create_or_rewrite(book):
    sheetname = askstring(title='New sheet', prompt='Enter the sheet name')
    if sheetname in book.sheetnames:
        ans = askyesno(title='Sheet is already exist', message='Rewrite?')
        if ans:
            return sheetname
        else:
            return create_or_rewrite(book)
    else:
        return sheetname

