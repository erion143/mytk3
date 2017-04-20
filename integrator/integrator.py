import os
import sys
import math
import numpy as np
import scipy.interpolate as iii
from tkinter import *

sys.path.append('..')

from graph3 import Deckart3, Line3
from mytk3 import TextWall
from myparser import parser
from tlib import make_weight


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
        self.plot.canvas.unbind('<Button-1>')
        self.plot.create_scale()
        self.e_number.pack()
        self.e_error.pack()
        self.canvas.pack()
        self.input = TextWindow(self.root)
        self.weights = TextWindow(self.root)
        self.pre_accept_points()

        self.active = False

    def mainloop(self):
        self.root.mainloop()

    def pre_accept_points(self, event=None):
        self.input.spawn()
        self.input.command = self.accept_points
        self.input.ready()
        self.root.unbind('<Control-o>')

    def accept_points(self, event=None):
        xs, ys = self.input.get()

        self.plot.add_group_of_points(xs, ys)
        self.input.despawn()
        self.active = True
        self.root.bind('<Control-s>', self.try_spline)
        self.root.bind('<Control-w>', self.ask_weight)

    def pre_try_spline(self, event=None):
        print('111111')
        points = sorted([p for p in self.plot.points if not p.is_basic()],
                        key=(lambda p: p.x))
        xs = [p.x for p in points]
        ys = [p.y for p in points]

        print(xs, len(xs))
        print(ys, len(ys))

        err = self.e_error.get()
        if err:
            err = float(err) * sum(ys)
        else:
            err = 0

        if self.weights.window:
            self.weights.accept()
        xxs, ws = self.weights.get()
        w = make_weight(xs, *(i for i in zip(xxs, ws)))
        return xs, ys, err, w

    def try_spline(self, event=None):
        xs, ys, err, w = self.pre_try_spline()
        print('w\t' + str(w))

        if err:
            spl = iii.UnivariateSpline(xs, ys, k=3, s=err, w=w)
        else:
            spl = iii.UnivariateSpline(xs, ys)
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

    def ask_weight(self, event=None):
        self.weights.spawn()
        self.root.unbind('<Control-w>')
        self.weights.window.protocol('WM_DELETE_WINDOW', self.foo)
        self.root.bind('<Control-r>', self.weights.get)

    def foo(self):
        print('protocol 2')
        self.weights.despawn()
        self.root.bind('<Control-w>', self.ask_weight)


class TextWindow:
    separator = '\t'
    pattern = (float, float)

    def __init__(self, master):
        self.master = master
        self.rows = []

        self.window = None
        self.text = None
        self.button = None
        self.command = None

    def mainloop(self):
        self.master.mainloop()

    def spawn(self, event=None):
        self.window = Toplevel(self.master)
        self.text = TextWall(self.window)
        self.text.pack()
        self.button = Button(self.window, text='accept')
        #self.button.pack()

        for row in self.rows:
            self.text.insert(END, row + '\n')

        # self.window.protocol('WM_DELETE_WINDOW', self.despawn)
        self.focus()

    def ready(self):
        self.button.pack()
        self.button.config(command=self.command)

    def accept(self, event=None):
        if self.text is not None:
            self.rows = [i for i in self.text.get('1.0', END).split('\n') if i]

        #print(self.rows)

    def despawn(self):
        print('protocol 1')
        self.accept()
        self.window.destroy()
        self.window = None
        self.text = None

    def get(self, event=None):
        self.accept()
        print('got it')
        if self.rows:
            print('path 1')
            data = parser(self.rows,
                          self.pattern,
                          separator=self.separator,
                          source_is_file=False)
        else:
            print('path 2')
            data = [[], []]
        #print(data)
        return data

    def focus(self):
        if self.window:
            self.window.focus()


def test_():
    root = Tk()
    tw = TextWindow(root)
    tw.mainloop()


if __name__ == '__main__':
    Container().mainloop()
    # test_()

