import os
import sys
import numpy as np
from scipy.interpolate import UnivariateSpline
from tkinter import *

sys.path.append('..')

from graph3 import Deckart3, Line3
from mytk3 import TextWall
from myparser import parser


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


class Container:
    def __init__(self):
        self.root = Tk()
        self.e_number = Entry(master=self.root)
        self.e_error = Entry(master=self.root)
        self.canvas = Canvas(self.root, width=600, height=400)
        self.plot = Deckart3(self.canvas)
        self.plot.create_scale()
        self.e_number.pack()
        self.e_error.pack()
        self.canvas.pack()
        self.tl = None
        self.text = None
        self.root.bind('<Control-o>', self.pre_accept_points)
        self.active = False

    def mainloop(self):
        self.root.mainloop()

    def pre_accept_points(self, event=None):
        self.tl = Toplevel(self.root)
        self.text = TextWall(self.tl)
        self.text.pack()
        self.tl.bind('<Control-r>', self.accept_points)
        self.root.unbind('<Control-o>')

    def accept_points(self, event=None):
        data = self.text.get(start_index='1.0', end_index=END)
        print(data)
        xs, ys = parser(data.split('\n'),
                        (float, float),
                        source_is_file=False,
                        loglevel='DEBUG')
        print(xs, ys)
        self.plot.add_group_of_points(xs, ys)
        self.tl.unbind('<Control-r>')
        self.tl.destroy()
        self.text = None
        self.tl = None
        self.active = True
        self.root.bind('<Control-s>', self.try_spline)

    def try_spline(self, event=None):
        points = sorted([p for p in self.plot.points if not p.is_basic()],
                        key=(lambda p: p.x))
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        err = self.e_error.get()
        if err:
            err = float(err) * sum(ys)
        else:
            err = 0
        spl = UnivariateSpline(xs, ys, s=err)
        xss = np.linspace(xs[0], xs[-1], 1000)
        yss = spl(xss)
        self.replace_line(xss, yss)

    def replace_line(self, xs, ys):
        if self.plot.lines:
            for line in self.plot.lines[:]:
                line.delete()
        Line3.from_coords(self.plot, xs, ys).replace()
        for point in self.plot.points:
            point.replace()

    def clear(self):
        if self.active:
            for point in self.plot.points[:]:
                point.delete()
            for line in self.plot.lines[:]:
                line.delete()
            self.root.bind('<Control-o>', self.pre_accept_points)


Container().mainloop()

