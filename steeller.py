from graph3 import Deckart3, Point3
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image
import os


MAX_WIDTH = 1700
MAX_HEIGHT = 900


class Container:
    def __init__(self):
        self.root = Tk()

        self.v_init = StringVar(self.root)
        self.e_init = Entry(self.root, textvariable=self.v_init)
        self.e_init.grid(row=0, column=0, columnspan=2, sticky=EW)
        self.b_simg = Button(self.root, text="Select image", command=self.f_img)
        self.b_simg.grid(row=1, column=0, sticky=E)
        self.b_init = Button(self.root, text="next >>", state=DISABLED)
        self.b_init.grid(row=1, column=1)

        self.canvas = Canvas(self.root)
        self.deck = Deckart3(self.canvas)
        self.deck.master.config(bg='#444444')
        self.deck.indent_config(20, 20, 30, 20)

        self.img = None

        self.xs = []
        self.ys = []

        self.b_add_x = Button(self.root, text='Add x', command=self.f_add_x)
        self.v_add_x = StringVar(self.root)
        self.e_add_x = Entry(self.root, textvariable=self.v_add_x)

        self.b_add_y = Button(self.root, text='Add y', command=self.f_add_y)
        self.v_add_y = StringVar(self.root)
        self.e_add_y = Entry(self.root, textvariable=self.v_add_y)

        self.b_go = Button(self.root, text="Go!", command=self.f_go)

        self.b_save = Button(self.root, text="Save", command=self.f_save)

        self.save_frame = Frame(self.root)
        self.b_rewrite = Button(self.save_frame, text="Rewrite", command=(lambda: self.write('w')))
        self.b_append = Button(self.save_frame, text="Append", command=(lambda: self.write('a')))
        self.b_cancel = Button(self.save_frame, text="cancel", command=self.f_cancel)

        self.b_cancel.pack(side=RIGHT)
        self.b_append.pack(side=RIGHT)
        self.b_rewrite.pack(side=RIGHT)

    def after_init(self):
        self.e_init.grid_forget()
        self.b_init.grid_forget()
        self.b_simg.grid_forget()

        self.canvas.grid(row=0, column=0, columnspan=3, sticky=NSEW)
        self.b_add_x.grid(row=1, column=0)
        self.e_add_x.grid(row=1, column=1, columnspan=2)
        self.b_add_y.grid(row=2, column=0)
        self.e_add_y.grid(row=2, column=1, columnspan=2)
        self.b_go.grid(row=3, column=2)

        self.deck.canvas.create_image(0, 0, anchor=NW, image=self.img)

    def __call__(self):
        self.root.mainloop()

    def f_img(self):
        self.v_init.set(askopenfilename(master=self.root))
        self.b_init.config(command=self.f_init, state=NORMAL)
        print('complete!')

    def f_init(self):
        flag = 0

        adr = self.v_init.get()
        foldr = os.path.split(adr)[0]
        os.chdir(foldr)
        img = Image.open(adr)
        width, height = img.size

        if height > MAX_HEIGHT:
            flag = 1
            width = int(MAX_HEIGHT / height * width)
            height = MAX_HEIGHT
        if width > MAX_WIDTH:
            flag = 1
            height = int(MAX_WIDTH / width * height)
            width = MAX_WIDTH

        if flag:
            img = img.resize((width, height), Image.LANCZOS)
            print('resize')
            print(width, height)

        width += (self.deck.indent.left + self.deck.indent.right)
        height += (self.deck.indent.top + self.deck.indent.bot)

        self.v_init.set(os.path.splitext(adr)[0] + '.gif')
        img.save(self.v_init.get())
        self.img = PhotoImage(file=self.v_init.get())

        self.canvas.config(width=width, height=height)
        self.after_init()

    def f_add_x(self):
        print('add x')
        self.deck.canvas.unbind('<Button-1>')
        self.deck.canvas.bind('<Button-1>', self.after_add_x)
        self.v_add_x.set('')
        self.e_add_x.focus()

    def after_add_x(self, event):
        self.deck.canvas.unbind('<Button-1>')
        x = float(self.v_add_x.get())
        xa = event.x
        self.xs.append([x, xa])

        if len(self.xs) > 1:
            self.xs.sort(key=(lambda l: l[0]))
            res = []
            for i in self.xs[1:]:
                res.append(left_x(self.xs[0], i))

            self.deck.x_min = sum(res) / len(res)

            k = (self.xs[0][0] - self.deck.x_min) / self.xs[0][1]

            xae = self.deck.canvas.winfo_width()
            if xae == 1 or xae == 0:
                xae = self.deck.canvas.winfo_reqwidth()

            self.deck.x_max = k * xae + self.deck.x_min

            print(self.deck.x_min, self.deck.x_max)

    def f_add_y(self):
        print('add y')
        self.deck.canvas.unbind('<Button-1>')
        self.deck.canvas.bind('<Button-1>', self.after_add_y)
        self.v_add_y.set('')
        self.e_add_y.focus()

    def after_add_y(self, event):
        self.deck.canvas.unbind('<Button-1>')
        y = float(self.v_add_y.get())
        ya = event.y
        self.ys.append([y, ya])

        if len(self.ys) > 1:
            self.ys.sort(key=(lambda l: l[0]), reverse=True)
            res = []
            for i in self.ys[1:]:
                res.append(top_y(self.ys[0], i))

            self.deck.y_max = sum(res) / len(res)

            k = (self.deck.y_max - self.ys[0][0]) / self.ys[0][1]

            ya0 = self.deck.canvas.winfo_height()
            if ya0 == 1 or ya0 == 0:
                ya0 = self.deck.canvas.winfo_reqheight()

            self.deck.y_min = self.deck.y_max - k * ya0

            print(self.deck.y_min, self.deck.y_max)

    def f_go(self):
        self.deck.canvas.unbind('<Button-1>')

        if len(self.xs) < 2 or len(self.ys) < 2:
            return 0

        self.b_add_x.grid_forget()
        self.b_add_y.grid_forget()
        self.e_add_x.grid_forget()
        self.e_add_y.grid_forget()
        self.b_go.grid_forget()
        self.b_save.grid(row=1, column=2, sticky=E)

        self.deck.canvas.bind('<Button-1>', self.f_place_point)
        self.deck.canvas.bind('<Button-3>', self.f_delete_point)

    def f_place_point(self, event):
        p = Point3.create_from_abs_coord(self.deck,
                                         event.x,
                                         event.y,
                                         radius=4,
                                         color='black')
        p.replace()

    def f_delete_point(self, event):
        point = self.deck.get_point(event)
        if point is None:
            return None
        else:
            point.delete()

    def f_save(self):
        self.b_save.grid_forget()
        self.save_frame.grid(row=1, column=1, columnspan=2, sticky=E)

    def write(self, mode):
        points = [[p.x, p.y] for p in self.deck.points]
        points.sort(key=(lambda l: l[0]))
        with open('results', mode) as f:
            if mode == 'a':
                for i in range(3):
                    f.write('\n')
            for p in points:
                f.write("{}\t{}\n".format(p[0], p[1]))

    def f_cancel(self):
        self.save_frame.grid_forget()
        self.b_save.grid(row=1, column=2, sticky=E)


def left_x(p1, p2):
    return (p2[1] * p1[0] - p1[1] * p2[0]) / (p2[1] - p1[1])


def top_y(p1, p2):
    return (p2[0] * p1[1] - p1[0] * p2[1]) / (p1[1] - p2[1])


if __name__ == '__main__':
    c = Container()
    c()
