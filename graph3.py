from tkinter import *
from random import random, randint

"""
Если вручную изменяется размер вложенного холста
то разметка осей глючит.
Необходимо переразметить их, чтобы все стало нормально.
"""


DEBUG = True


class Deckart3:
    def __init__(self, master):
        self.master = master

        if DEBUG:
            self.master.config(bg='#ee0000')

        self.indent = Indent(self.master)

        self.modifier = Modifier(self)
        self.width, self.height = self.get_size()

        self.canvas = Canvas(master=self.master.master,
                             width=self.width,
                             height=self.height,
                             bd=0,
                             highlightthickness=0)
        if DEBUG:
            self.canvas.config(bg='#eeeeee')

        self.main_ind = self.master.create_window(self.indent.left,
                                                  self.indent.top,
                                                  anchor=NW,
                                                  window=self.canvas)

        self.canvas.bind('<Button-1>', self.choose_point)

        # Minimum and maximum of coordinates
        self.x_min = 0
        self.x_max = 10
        self.y_min = 0
        self.y_max = 10

        # Arrays for points and lines
        self.points = []
        self.lines = []

        # TEST
        self.master.bind('<Configure>', self.size_config)
        self.scale = None

    def create_scale(self):
        if self.scale is None:
            self.scale = DScale3(self)

    def get_size(self):
        x = self.indent.get_width() - self.indent.left - self.indent.right
        y = self.indent.get_height() - self.indent.top - self.indent.bot
        return x, y

    def get_xs(self):
        res = [p.x for p in self.points]
        for line in self.lines:
            res += line.get_xs()
        return res

    def get_ys(self):
        res = [p.y for p in self.points]
        for line in self.lines:
            res += line.get_ys()
        return res

    def get_coord(self, absx, absy):
        x = absx / self.width * (self.x_max - self.x_min) + self.x_min
        y = (self.height - absy) / self.height * (self.y_max - self.y_min) + self.y_min
        return x, y

    def get_abs_coord(self, x, y):
        absx = self.width * (x - self.x_min) / (self.x_max - self.x_min)
        absy = self.height * (self.y_max - y) / (self.y_max - self.y_min)
        return absx, absy

    def replot(self):
        for p in self.points:
            p.get_abs_coords()
            p.replace()

        for l in self.lines:
            for p in l.points:
                p.get_abs_coords()
            l.replace()

    def indent_config(self, top=None, bot=None, left=None, right=None):
        if top is not None:
            self.master.move(self.main_ind, 0, top-self.indent.top)
            print("move plot at {} pxs on x".format(top-self.indent.top))
            self.indent.top = top
        if left is not None:
            self.master.move(self.main_ind, left-self.indent.left, 0)
            print("move plot at {} pxs on y".format(left-self.indent.left))
            self.indent.left = left
        if bot is not None:
            self.indent.bot = bot
        if right is not None:
            self.indent.right = right

        self.size_config()
        print("Canvas coordinates:", self.master.coords(self.main_ind))

    def size_config(self, event=None):
        self.width, self.height = self.get_size()
        self.canvas.config(width=self.width, height=self.height)
        print("CONFIG!")
        print(self.width, self.height)
        self.replot()  # перестроить объекты
        self.modifier.replace()  # перестроить движимые объекты
        self.scale.update()

    def auto_scale(self):
        print('\t\tlet\'s start auto_scale!!!')
        xs = self.get_xs()
        xs.sort()
        ys = self.get_ys()
        ys.sort()
        self.x_min = xs[0]
        self.y_min = ys[0]
        self.x_max = xs[-1]
        self.y_max = ys[-1]
        self.scale.make_points(coe=.1)
        self.replot()  # перестроить объекты
        self.modifier.replace()  # перестроить движимые объекты

    def is_coord_in_plot(self, x, y):
        if x < self.x_min:
            ret_x = -1
        elif x > self.x_max:
            ret_x = 1
        else:
            ret_x = 0
        if y < self.y_min:
            ret_y = -1
        elif y > self.y_max:
            ret_y = 1
        else:
            ret_y = 0
        return ret_x, ret_y

    def add_point(self, x, y):
        ret_x, ret_y = self.is_coord_in_plot(x, y)
        if ret_x < 0:
            self.x_min = x
        elif ret_x > 0:
            self.x_max = x
        if ret_y < 0:
            self.y_min = y
        elif ret_y > 0:
            self.y_max = y
        if ret_x or ret_y:
            self.scale.make_points()
            self.replot()  # перестроить объекты
            self.modifier.replace()  # перестроить движимые объекты

        p = Point3(self, x, y)
        p.replace()

    def correct_by_group_of_points(self, xs, ys):
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        ret_min_x, ret_min_y = self.is_coord_in_plot(min_x, min_y)
        ret_max_x, ret_max_y = self.is_coord_in_plot(max_x, max_y)
        if ret_min_x < 0:
            self.x_min = min_x
        if ret_max_x > 0:
            self.x_max = max_x
        if ret_min_y < 0:
            self.y_min = min_y
        if ret_max_y > 0:
            self.y_max = max_y
        if ret_min_x or ret_min_y or ret_max_x or ret_max_y:
            self.replot()
            self.modifier.replace()
            self.scale.make_points()

    def add_group_of_points(self, xs, ys):
        self.correct_by_group_of_points(xs, ys)

        for x, y in zip(xs, ys):
            p = Point3(self, x, y)
            p.replace()

    def catch_point(self, event):
        print("choose point")
        inds = [i.ind for i in self.points]
        indr = self.canvas.find_closest(event.x, event.y)
        ind = bust(indr, inds)
        print(ind)
        if ind == -1:
            return None
        else:
            return ind

    def get_point(self, event):
        ind = self.catch_point(event)
        if ind is not None:
            return self.points[ind]
        else:
            return None

    def choose_point(self, event):
        point = self.get_point(event)
        if point is None:
            return None
        else:
            point.choose()

    def get_chosen_points(self):
        return [p for p in self.points if p.chosen]

    def choose_line(self, event):
        inds = [l.ind for l in self.lines]
        indr = self.canvas.find_closest(event.x, event.y)
        if not inds:
            return None
        else:
            ind = bust(inds, indr)
            if ind == -1:
                return None
            else:
                return self.lines[ind]

    def t_plot_line_by_selected_points(self):
        point_list = self.get_chosen_points()
        point_list.sort(key=(lambda p: p.x))

        l = Line3(self, point_list)
        l.replace()

    def temp(self, event):
        line = self.choose_line(event)
        if line:
            self.canvas.unbind('<ButtonRelease-1>')

            self.modifier.accept(line)
            self.modifier.fill(color='#55ee55', radius=6)
            self.modifier.replace()
            self.modifier.run()


class Indent:
    def __init__(self, canvas):
        self.canvas = canvas
        self.top = 40
        self.bot = 40
        self.left = 80
        self.right = 40

    def get_height(self):
        h = self.canvas.winfo_height()
        if h < 2:
            return self.canvas.winfo_reqheight()
        else:
            return h

    def get_width(self):
        w = self.canvas.winfo_width()
        if w < 2:
            return self.canvas.winfo_reqwidth()
        else:
            return w
    """
    В _bot и _right единица вычитается так как, по идее, возвращается координата
    крайнего пикселя вложенного холста
    """
    def get_bot(self):
        return self.get_height() - self.bot - 1

    def get_right(self):
        return self.get_width() - self.right - 1

    def get_left(self):
        return self.left

    def get_top(self):
        return self.top


class DScale3:
    def __init__(self, plot, width=2):
        self.plot = plot
        self.canvas = self.plot.master
        self.width = width
        self.plot_width, self.plot_height = self.plot.get_size()

        self.x_min = 0
        self.x_max = 0
        self.y_min = 0
        self.y_max = 0

        self.x = None
        self.y = None
        self.xs = []
        self.ys = []

        self.update_key_points()
        self.update_lines()
        self.make_points()

        self.flag = True
        self.x_count = 0  # Число меток на оси х
        self.y_count = 0  # Число меток на оси y

        self.moves = 0  # Число перемещений меток на осях

        self.canvas.master.bind('<Control-a>', self.make_points)

    def update_key_points(self):
        self.x_min = self.plot.indent.get_left() - 1
        self.x_max = self.plot.indent.get_right() + 1
        self.y_min = self.plot.indent.get_bot() + 1
        self.y_max = self.plot.indent.get_top() - 1

    def update_lines(self):
        print('\t\tupdate lines')
        if self.x:
            self.canvas.delete(self.x)
        if self.y:
            self.canvas.delete(self.y)

        self.x = self.canvas.create_line(self.x_min - 1,  # дабы оси перекрывались
                                         self.y_min + self.width // 2,  # при четной щирине координата -
                                                                        # середина снизу
                                         self.x_max + 1,
                                         self.y_min + self.width // 2,
                                         width=self.width)

        self.y = self.canvas.create_line(self.x_min,  # при четной щирине координата -
                                                      # середина справа
                                         self.y_min + 2,  # линия ведется до этой точки не включая
                                                          # + дабы оси перекрывались
                                         self.x_min,
                                         self.y_max,
                                         width=self.width)

        print("x_axis created!")
        print(self.x_min,
              self.y_min + self.width // 2,
              self.x_max,
              self.y_min + self.width // 2)

    def update(self):
        print('\taxes update')
        self.update_key_points()
        self.update_lines()
        if self.flag:
            self.flag = not self.flag
            self.canvas.after(500, self.sub_move)

            # Полезная идея но пока глючит
            # if self.moves < 11:
            #     self.canvas.after(250, self.sub_move)
            # else:
            #     self.moves = 0
            #     self.canvas.after(250, self.make_x_points)

    def sub_move(self):
        new_width, new_height = self.plot.get_size()
        kx = new_width / self.plot_width
        ky = new_height / self.plot_height
        for x in self.xs:
            x.move(kx)
        for y in self.ys:
            y.move(ky)

        self.plot_width = new_width
        self.plot_height = new_height

        self.moves += 1
        self.flag = True

    def make_points(self, event=None, coe=0):
        self.make_x_points(coe=coe)
        self.make_y_points(coe=coe)

    def make_x_points(self, coe=0):
        for x in self.xs:
            x.delete()

        self.xs = []
        xs = self.plot.get_xs()
        if coe:
            xs[0] -= coe * xs[0]
            xs[-1] += coe * xs[-1]
        if not xs or len(xs) == 1:
            xs = [self.plot.x_min, self.plot.x_max]

        print("xs = {}".format(xs))
        fnz, left, right = interval_limits(xs)
        print("fnz, left, right = {}, {}, {}".format(fnz, left, right))
        step, count = grid_spacing(fnz, left, right)
        self.x_count = count
        self.plot.x_min, self.plot.x_max = left, right

        abs_step = self.plot.get_size()[0] / (count - 1)

        for i in range(count):
            self.xs.append(DScalePointX(self,
                                        int(i * abs_step),
                                        left + i * step))

        for x in self.xs:
            x.place()

    def make_y_points(self, coe):
        for y in self.ys:
            y.delete()

        self.ys = []
        ys = self.plot.get_ys()
        if coe:
            ys[0] -= ys[0] * coe
            ys[-1] += ys[-1] * coe
        if not ys or len(ys) == 1:
            ys = [self.plot.y_min, self.plot.y_max]

        print("ys = {}".format(ys))
        fnz, left, right = interval_limits(ys)
        print("fnz, left, right = {}, {}, {}".format(fnz, left, right))
        step, count = grid_spacing(fnz, left, right)
        self.y_count = count
        self.plot.y_min, self.plot.y_max = left, right

        abs_step = self.plot.get_size()[1] / (count - 1)

        for i in range(count):
            self.ys.append(DScalePointY(self,
                                        int(i * abs_step),
                                        right - i * step))

        for y in self.ys:
            y.place()


class DScalePoint:
    def __init__(self, scale, displacement, label):
        self.scale = scale
        self.canvas = scale.canvas
        self.plot = scale.plot
        self.disp = displacement
        self.label = round(label, 2)

        self.ind = None
        self.lind = None

    def delete(self):
        if self.ind is not None:
            self.canvas.delete(self.ind)
            self.canvas.delete(self.lind)

    def place(self):
        if self.ind is not None:
            self.canvas.delete(self.ind)
            self.canvas.delete(self.lind)


class DScalePointX(DScalePoint):
    def __init__(self, scale, displacement, label):
        DScalePoint.__init__(self, scale, displacement, label)
        self.plot_width = self.plot.get_size()[0]
        self.plot_height = self.plot.indent.get_bot()

    def place(self):
        DScalePoint.place(self)

        x0 = self.plot.indent.get_left() + self.disp
        y0 = self.plot.indent.get_bot()
        y1 = y0 + 10

        self.ind = self.canvas.create_line(x0, y0, x0, y1)
        self.lind = self.canvas.create_text(x0, y1+7, text=self.label, anchor=N)

    def move(self, k):
        y = self.plot.indent.get_bot()
        new_disp = int(round(self.disp * k, 0))

        moves = (new_disp - self.disp,
                 y - self.plot_height)

        self.canvas.move(self.ind, *moves)
        self.canvas.move(self.lind, *moves)

        self.disp = new_disp
        self.plot_height = y


class DScalePointY(DScalePoint):
    def __init__(self, scale, displacement, label):
        DScalePoint.__init__(self, scale, displacement, label)

    def place(self):
        DScalePoint.place(self)

        x1 = self.plot.indent.get_left()
        x0 = x1 - 10
        y = self.plot.indent.get_top() + self.disp

        self.ind = self.canvas.create_line(x0, y, x1, y)
        self.lind = self.canvas.create_text(x0 - 7, y, text=self.label, anchor=E)

    def move(self, k):
        new_disp = int(round(k * self.disp, 0))

        moves = new_disp - self.disp

        self.canvas.move(self.ind, 0, moves)
        self.canvas.move(self.lind, 0, moves)

        self.disp = new_disp


class Modifier:
    def __init__(self, master):
        self.master = master

        self.line = None
        self.newline = None
        self.points = []

        self.before_move = None
        self.after_move = None

    def accept(self, line):
        self.line = line

    def fill(self, **kwargs):
        if not self.line:
            return None
        else:
            for p in self.line.points:
                new_p = Point3.create_from_point(p,
                                                 parent=p,
                                                 storage=self.points,
                                                 **kwargs)
                self.points.append(new_p)

            self.newline = Line3(self.master,
                                 self.points,
                                 color='#eea500',
                                 width=3,
                                 smooth=1)
            self.newline.replace()      # Сперва перерисовываем линию

            self.replace()              # Затем точки

    def replace(self):
        for p in self.points:
            p.replace()

    def save(self):
        print('\nLet\'s go save!\n')
        for p in self.points:
            p.parent.on_move(p.absx, p.absy)
            self.line.replace()

    def catch_point(self, event):
        inds = [p.ind for p in self.points]
        if not inds:
            return None
        indr = self.master.canvas.find_closest(event.x, event.y)
        ind = bust(indr, inds)
        if ind == -1:
            return None
        else:
            return ind

    def select_point_here(self, event):
        ind = self.catch_point(event)
        if ind is None:
            return None
        else:
            return self.points[ind]

    def f_before_move(self, event):
        print("Before")
        self.before_move = event

    def f_move(self, event):
        print("After")
        self.after_move = event
        self.f_after_move()

    def f_after_move(self):
        print("After move")
        if self.before_move is None:
            return None

        p = self.select_point_here(self.before_move)

        if p is None:
            return None
        else:
            p.on_move(p.absx,
                      self.after_move.y)
            self.newline.replace()
            self.replace()  # VERY BAD!

    def run(self):
        self.master.canvas.bind('<Button-1>', self.f_before_move)
        self.master.canvas.bind('<ButtonRelease-1>', self.f_move)
        print("Modification available")

    def stop(self):
        self.line = None
        self.newline.delete()
        self.newline = None
        for p in self.points:
            p.delete(not_rm=True)

        self.points = []

        self.master.canvas.unbind('<Button-1>')
        self.master.canvas.unbind('<ButtonRelease-1>')


class BasicPoint3:
    def __init__(self, master, x, y, abs_=None):
        self.master = master

        self.x = x
        self.y = y

        if abs_:
            self.absx, self.absy = abs_
        else:
            self.get_abs_coords()

    def get_abs_coords(self):
        self.absx, self.absy = self.master.get_abs_coord(self.x, self.y)

    def __repr__(self):
        return "BasicPoint ({}, {})".format(self.x, self.y)

    @staticmethod
    def create_from_abs_coord(master, absx, absy):
        x, y = master.get_coord(absx, absy)
        return BasicPoint3(master, x, y, (absx, absy))

    def on_move(self, new_absx, new_absy):
        flag = 0
        self.absx = new_absx
        self.absy = new_absy
        self.x, self.y = self.master.get_coord(self.absx, self.absy)

        if self.x > self.master.x_max:
            self.x = self.master.x_max
        elif self.x < self.master.x_min:
            self.x = self.master.x_min
        else:
            flag += 1
        if self.y > self.master.y_max:
            self.y = self.master.y_max
        elif self.y < self.master.y_min:
            self.y = self.master.y_min
        else:
            flag += 1

        if flag != 2:
            self.get_abs_coords()


class Point3(BasicPoint3):
    def __init__(self, master, x, y, abs_=None,
                 color='#dd2222', radius=3,
                 storage=None,
                 parent=None):
        BasicPoint3.__init__(self, master, x, y, abs_)

        self.parent = parent
        self.storage = storage

        self.color = color
        self.ccolor = '#' + color[:0:-1]
        self.r = radius

        self.ind = None
        self.visible = True
        self.chosen = False

        if storage is None:
            self.storage = self.master.points

        self.storage.append(self)
        print(id(self.storage))

    @staticmethod
    def create_from_abs_coord(master, absx, absy, **kwargs):
        x, y = master.get_coord(absx, absy)
        return Point3(master, x, y, (absx, absy), **kwargs)

    @staticmethod
    def create_from_point(point, *args, **kwargs):
        x = point.x
        y = point.y
        master = point.master

        if args:
            for i in args:
                kwargs[i] = getattr(point, i)

        return Point3(master, x, y, **kwargs)

    @staticmethod
    def add_point_on_plot(master, x, y):
        p = Point3(master, x, y)
        p.replace()
        return p

    def replace(self):
        if self.ind:
            self.master.canvas.delete(self.ind)
            if not self.visible:
                self.ind = None

        if self.visible:
            self.ind = self.master.canvas.create_oval(self.absx - self.r,
                                                      self.absy - self.r,
                                                      self.absx + self.r,
                                                      self.absy + self.r,
                                                      fill=self.color)

    def switch(self):
        self.visible = not self.visible

    # def __del__(self):
    #     if self.ind:
    #         self.master.canvas.delete(self.ind)
    #     self.storage.remove(self)

    def delete(self, not_rm=False):
        if self.ind:
            self.master.canvas.delete(self.ind)
        if not not_rm:
            self.storage.remove(self)

    def choose(self):
        self.color, self.ccolor = self.ccolor, self.color
        self.chosen = not self.chosen
        self.replace()

    def on_move(self, new_absx, new_absy):
        BasicPoint3.on_move(self, new_absx, new_absy)
        self.replace()

    def __repr__(self):
        s = "Point ({}, {})".format(self.x, self.y)
        return s


class Line3:
    def __init__(self, master, points, **kwargs):
        self.master = master
        self.points = [p for p in points]

        self.master.lines.append(self)

        self.ind = None
        self.visible = True
        self.color = kwargs.get('color', '#111111')
        self.width = kwargs.get('width', 2)
        self.smooth = kwargs.get('smooth', 0)

        print("create line {}".format(self))

    @staticmethod
    def from_coords(master, xs, ys):
        points = []

        for x, y in zip(xs, ys):
            p = BasicPoint3(master, x, y)

            points.append(p)

        return Line3(master, points)

    def get_xs(self):
        return [p.x for p in self.points]

    def get_ys(self):
        return [p.y for p in self.points]

    def get_abs_coords(self):
        print('self.points from abs coords:', self.points)
        res = []

        for p in self.points:
            res += [p.absx, p.absy]

        return res

    def replace(self, **kwargs):
        if self.ind:
            self.master.canvas.delete(self.ind)
            if not self.visible:
                self.ind = None

        print(self.get_abs_coords())

        if self.visible:
            self.ind = self.master.canvas.create_line(*self.get_abs_coords(),
                                                      fill=self.color,
                                                      width=self.width,
                                                      smooth=self.smooth,
                                                      **kwargs)

    def delete(self):
        if self.ind:
            self.master.canvas.delete(self.ind)

        self.master.lines.remove(self)

    def create_service_points(self):
        pass


class TestContainer:
    def __init__(self):
        self.root = Tk()
        self.c = Canvas(self.root, height=400, width=500, bd=0,
                        highlightthickness=0)
        self.c.grid(row=0, column=0, rowspan=4, columnspan=3, sticky=NSEW)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.d = Deckart3(self.c)
        self.d.create_scale()

        self.b_add_random = Button(self.root,
                                   text='Random add',
                                   width=10,
                                   command=self.f_add_random)
        self.b_add_random.grid(row=4, column=0, sticky=W)

        self.x = StringVar(self.root)
        self.y = StringVar(self.root)

        self.b_add = Button(self.root,
                            text='Add',
                            width=10,
                            command=self.f_add)
        self.b_add.grid(row=5, column=0, sticky=W)

        self.e_x = Entry(self.root, textvariable=self.x)
        self.e_x.grid(row=5, column=1, sticky=EW)
        self.e_y = Entry(self.root, textvariable=self.y)
        self.e_y.grid(row=5, column=2, sticky=EW)

        self.b_add_line = Button(self.root, text="Add line", command=self.f_add_line)
        self.b_add_line.grid(row=6, column=0, columnspan=2)
        self.b_width = Button(self.root, text='=>', command=self.f_width)
        self.b_width.grid(row=6, column=1)

        self.b_start_mod = Button(self.root, text='Mod', command=self.f_mod)
        self.b_start_mod.grid(row=7, column=0)

        self.b_save = Button(self.root, text="Save")
        self.b_save.grid(row=7, column=1)

    def f_width(self):
        w = self.d.canvas.winfo_reqwidth()
        self.d.canvas.config(width=(w+10))
        self.d.replot()

    def f_add_random(self):
        x = round(randint(0, 8) + random(), 3)
        y = round(randint(0, 8) + random(), 3)
        self.d.add_point(x, y)
        print("{} added".format(self.d.points[-1]))

    def f_add(self):
        x = float(self.x.get().replace(',', '.'))
        y = float(self.y.get().replace(',', '.'))
        self.d.add_point(x, y)
        print("{} added".format(self.d.points[-1]))

    def f_add_line(self):
        for l in self.d.lines:
            l.delete()
        self.d.t_plot_line_by_selected_points()

    def __call__(self):
        self.root.mainloop()

    def f_mod(self):
        self.d.canvas.bind('<ButtonRelease-1>', self.d.temp)
        self.b_save.config(command=self.f_save)

    def f_save(self):
        self.d.modifier.save()
        self.d.modifier.stop()


def bust(values_list, target_list):
    for el in values_list:
        try:
            ind = target_list.index(el)
        except ValueError:
            continue
        else:
            return ind
    else:
        return -1


def first_non_zero(num):
    """
    first_non_zero(1.1) == 0
    first_non_zero(0.1) == -1
    :param num:
    :return:
    """

    if num == 0:
        return 1
    num1 = str(abs(num)).replace(',', '.')

    def ifmore(num):
        foo = num.split('.')[0]
        return len(foo) - 1

    def ifless(num):
        num = num[2:]
        res = 1
        for i in num:
            if i == '0':
                res += 1
            else:
                break
        return res * -1

    if num > 0:
        return ifmore(num1)
    else:
        return ifless(num1)


def round_up(num, digit):
    def ifless(num, digit):
        res = round(num, digit)

        if res < num:
            res += 10 ** (digit * -1)

        return round(res, digit)

    def ifmore(num, digit):
        res = int(num)
        for i in range(digit):
            res //= 10
        out = res * 10 ** digit
        if out == num:
            return float(out)
        else:
            return float((res + 1) * 10 ** digit)

    if digit > 0:
        return ifmore(num, digit)
    else:
        return ifless(num, digit * -1)


def interval_limits(l):
    """
    left - граница слева
    right - граница справа
    :param l:
    :return:
    """
    mmin = min(l)
    mmax = max(l)
    length = mmax - mmin
    fnz = first_non_zero(length)
    left = round_up(mmin, fnz)
    if left != mmin:
        left -= 10 ** fnz
    right = round_up(mmax, fnz)
    return fnz, left, right


def grid_spacing(fnz, left, right):
    basic = [.1, .25, .5, 1.0][::-1]

    for i in basic:
        res = [left]
        step = (10 ** fnz) * i

        while res[-1] < right:
            res.append(round(res[-1] + step, 2))

        print(res)
        if len(res) < 7:
            continue
        else:
            return step, len(res)


if __name__ == '__main__':
    print(round_up(10, 1))
    t = TestContainer()
    t()
