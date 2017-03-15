import shelve
from tkinter import *


class TextWall(Frame):
    def __init__(self, parent, **conf):
        Frame.__init__(self, parent)
        sbar = Scrollbar(self)
        text = Text(self, **conf)

        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)

        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, fill=BOTH, expand=YES)

        self.sbar = sbar
        self.text = text

    def config(self, **conf):
        self.text.config(**conf)

    def get(self, start_index, end_index):
        return self.text.get(start_index, end_index)

    def insert(self, index, text):
        self.text.insert(index, text)

    def clear(self):
        self.text.delete('1.0', END)

    def delete(self, start, end):
        self.text.delete(start, end)

    def copy(self):
        print('copy')
        try:
            txt = self.text.get(SEL_FIRST, SEL_LAST)
        except TclError:
            return None
        else:
            self.clipboard_clear()
            self.clipboard_append(txt)

    def paste(self):
        try:
            pst = self.clipboard_get()
        except TclError:
            return None
        try:
            self.text.delete(SEL_FIRST, SEL_LAST)
        except TclError:
            pass
        finally:
            self.insert(INSERT, pst)


class ScrollableFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)

        self.cv = cv = Canvas(master=self, width=300, height=100)
        cv.pack(side=LEFT, fill=BOTH, expand=YES)

        self.sb = sb = Scrollbar(master=self)
        sb.pack(side=RIGHT, fill=Y)

        cv.config(yscrollcommand=sb.set)
        sb.config(command=cv.yview)

        self.fr = fr = Frame(cv, height=100, width=300, bd=0)
        self.fr_id = cv.create_window(0, 0, window=fr, anchor=NW)

        cv.bind('<Configure>', self.canvas_configure)
        fr.bind('<Configure>', self.frame_configure)

    def frame_configure(self, event):
        size = (self.fr.winfo_reqwidth(), self.fr.winfo_reqheight())
        self.cv.config(scrollregion="0 0 %s %s" % size)
        if self.cv.winfo_width() != size[0]:
            self.cv.config(width=size[0])

    def canvas_configure(self, event):
        if self.cv.winfo_width() != self.fr.winfo_reqwidth():
            self.cv.itemconfigure(self.fr_id, width=self.cv.winfo_width())

    def get_inner_frame(self):
        return self.fr

    @staticmethod
    def place(master, **kwargs):
        ret = ScrollableFrame(master, **kwargs)
        return ret, ret.fr


class ListWall(Frame):
    def __init__(self, parent, options, **conf):
        Frame.__init__(self, parent, **conf)
        self.sbar = sbar = Scrollbar(self)
        self.lst = lst = Listbox(self)
        sbar.config(command=lst.yview)
        lst.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        lst.config(selectmode=SINGLE)  # else BROWSE, MULTIPLE, EXTENDED
        self.selmod = SINGLE
        lst.pack(side=LEFT, expand=YES, fill=BOTH)
        self.makelist(options)

    def curselection(self):
        return self.lst.curselection()

    def get(self, index):
        return tuple(self.lst.get(ind) for ind in index)

    def makelist(self, options):
        pos = 0
        for label in options:
            self.lst.insert(pos, label)
            pos += 1

    def add(self, name):
        self.lst.insert(END, name)

    def clear(self):
        self.lst.delete(0, END)

    def delete(self, ind):
        self.lst.delete(ind)


'''
class CheckWall(Frame):
    def __init__(self, parent, label, options, packdict={'side': TOP}, **conf):
        Frame.__init__(self, parent, **conf)
        self.pack(**packdict)
        self.lab = Label(self, text=label)
        self.lab.pack(side=TOP, fill=X)
        self.buttons = {}
        self.makebuttons(options)

    def makebuttons(self, options):
        for name, var in options:
            c = Checkbutton(self,
                            text=name,
                            variable=var)
            c.pack()
            self.buttons[name] = (c, var)

    def select(self, name):
        self.buttons[name][0].select()

    def deselect(self, name):
        self.buttons[name][0].deselect()
'''


class MyCheckWall(ScrollableFrame):
    def __init__(self, master, **kwargs):
        ScrollableFrame.__init__(self, master, **kwargs)
        self.buttons = {}
        self.c_row = 0

    def add_checkbox(self, name, var):
        c = Checkbutton(self.fr,
                        text=name,
                        variable=var)
        c.grid(row=self.c_row, sticky=W)
        self.buttons[name] = (c, var)
        self.c_row += 1

    def delete(self, name):
        self.buttons[name][1].grid_forget()
        self.buttons.pop(name)
        self.c_row -= 1

    def ask(self, name):
        return self.buttons[name][1].get()

    def ask_all(self):
        return (i[1].get() for i in self.buttons)

    def select(self, name):
        self.buttons[name][0].select()

    def deselect(self, name):
        self.buttons[name][0].deselect()

    @staticmethod
    def place(master, **kwargs):
        ret = MyCheckWall(master, **kwargs)
        return ret, ret.fr


class SingleCheckBox(Frame):
    def __init__(self, parent, name, var=None, **conf):
        Frame.__init__(self, parent, **conf)
        if var is None:
            self.var = IntVar(master=parent)
        else:
            self.var = var
        self.ch = Checkbutton(self,
                              text=name,
                              variable=self.var)
        self.ch.pack(expand=YES, fill=BOTH)

    def select(self):
        self.ch.select()

    def deselect(self):
        self.ch.deselect()


class StorageList(Frame):
    def __init__(self, parent, st_name, **conf):
        Frame.__init__(self, parent, **conf)

        sbar = Scrollbar(self)
        lst = Listbox(self)
        sbar.config(command=lst.yview)
        lst.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        lst.pack(side=LEFT, fill=BOTH, expand=YES)
        self.lst = lst
        self.sbar = sbar

        self.st_name = st_name

        self.fill_list()

    def fill_list(self):
        with shelve.open(self.st_name) as store:
            for key in store.keys():
                self.lst.insert(END, key)

    def refresh(self):
        self.lst.delete(0, END)
        self.fill_list()


class RadioWall(LabelFrame):
    def __init__(self, master, text, variable, *variants):
        LabelFrame.__init__(self, master, text=text)
        self.variable = variable
        self.buttons = {}
        for button in variants:
            b = Radiobutton(master=self,
                            text=button,
                            variable=self.variable,
                            value=button)
            b.pack(anchor=W)
            self.buttons[button] = b
        self.buttons[variants[0]].select()

    def get(self):
        return self.variable.get()

    def select(self, button):
        self.buttons[button].select()


def make_basic_menu(parent):
    """
    Функция написана в целом как шпаргалка по работе с меню.
    :param parent: master widget
    :return: top level menu
    """
    top = Menu(parent)
    parent.config(menu=top)
    file = Menu(top, tearoff=False)
    file.add_separator()
    file.add_command(label='Quit', command=parent.quit, underline=0)
    top.add_cascade(label='Файл', menu=file, underline=0)
    return top


def mk_buttons(parent, store, buttons):
    for name, action in buttons:
        b = Button(master=parent, text=name)
        if action is not None:
            b.config(command=action)
        store.append(b)


if __name__ == '__main__':
    labels = []
    root = Tk()
    scrf, fr = MyCheckWall.place(root)
    scrf.pack(fill=BOTH, expand=YES)

    def add_button():
        print()
        scrf.add_checkbox("checkbutton #{}".format(len(scrf.buttons.keys())), IntVar(root))

    b = Button(root, text="add", command=add_button)
    b.pack()

    v = StringVar()
    rb = RadioWall(root, "test", v, "fir", "sec", "thir")
    rb.pack(expand=YES, fill=BOTH)

    b2 = Button(root, text='print', command=(lambda v=v: print(v.get()))).pack()

    e1 = Entry(root)
    e1.pack()

    e2 = Entry(root)
    e2.pack()

    active = 1

    def f1(event=None):
        e2.focus()

    def f2(event=None):
        e1.focus()

    e1.bind('<Tab>', f1)
    e2.bind('<Shift-Tab>', f2)

    root.mainloop()
