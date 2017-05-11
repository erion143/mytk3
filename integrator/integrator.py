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
from tlib import make_weight, integrator, speed


class Container:
    test = True

    def __init__(self):
        self.root = Tk()
        self.e_number = Entry(master=self.root)
        self.e_error = Entry(master=self.root)
        self.l_number = Label(self.root, text='Number of points')
        self.l_error = Label(self.root, text='Error')
        self.l_coord = Label(master=self.root)

        self.l_number.grid(row=0, column=0)
        self.e_number.grid(row=0, column=1)
        self.l_error.grid(row=1, column=0)
        self.e_error.grid(row=1, column=1)
        self.l_coord.grid(row=0, column=2, rowspan=2)

        self.canvas = Canvas(self.root, width=600, height=400)
        self.canvas.grid(row=2, column=0, columnspan=3, sticky=NSEW)
        self.plot = Deckart3(self.canvas)
        self.plot.canvas.unbind('<Button-1>')
        self.plot.create_scale()

        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(2, weight=1)

        self.input = TextWindow(self.root)
        self.weights = TextWindow(self.root)

        self.active = False
        self.actual = None  # Для сплайна

        self.pre_accept_points()

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
        self.root.bind('<Control-q>', self.integrate)
        self.root.bind('<Control-c>', self.to_clipboard)

    def get_counts(self):
        ret = self.e_number.get()
        if not ret:
            ret = 0
        else:
            ret = int(ret)

        return ret

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
        if not ws:
            w = None
        else:
            w = make_weight(xs, *(i for i in zip(xxs, ws)))
        print('ws', ws)
        return xs, ys, err, w

    def try_spline(self, event=None):
        xs, ys, err, w = self.pre_try_spline()
        print('w\t' + str(w))

        if err:
            spl = iii.UnivariateSpline(xs, ys, k=3, s=err, w=w)
        else:
            spl = iii.UnivariateSpline(xs, ys)

        num = self.get_counts()
        if not num:
            xss = xs
        else:
            xss = np.linspace(xs[0], xs[-1], num)
        yss = spl(xss)
        self.replace_line(xss, yss)
        print(len(self.plot.points))

    def replace_line(self, xs, ys):
        if self.plot.lines:
            for line in self.plot.lines[:]:
                line.delete()
        self.actual = Line3.from_coords(self.plot, xs, ys)
        self.actual.replace()
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
        self.plot.canvas.bind('<Button-1>', self.show_x)

    def foo(self):
        print('protocol 2')
        self.weights.despawn()
        self.root.bind('<Control-w>', self.ask_weight)
        self.l_coord.config(text='')
        self.plot.canvas.unbind('<Button-1>')

    def show_x(self, event):
        x, _ = self.plot.get_coord(event.x, event.y)
        self.l_coord.config(text=str(x))
        xx = round(x, 2)
        self.root.clipboard_clear()
        self.root.clipboard_append(str(xx))

    def integrate(self, event):
        xs = [p.x for p in self.actual.points]
        ys = [p.y for p in self.actual.points]
        ss = [integrator(xs, ys, x_max=x) for x in xs]
        print(xs)
        print(ss)

    def to_clipboard(self, event=None):
        print('START TO CLIPBOARD')
        xs, ys, err, ws = self.pre_try_spline()
        spl = iii.UnivariateSpline(xs, ys, k=3, s=err, w=ws)

        xxs, yys = speed(xs, spl(xs))

        res = ''
        for x, y in zip(xxs, yys):
            res += '{}\t{}\n'.format(x, y)

        self.root.clipboard_clear()
        self.root.clipboard_append(res)


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


class TestSpeed:
    def __init__(self, master):
        self.master = master
        self.times = []
        self.vols = []
        self.vols_ = []
        self.speed = []

        self.vols_line = None
        self.speed_line = None

    def accept(self, times, vols):
        self.vols = vols
        self.times = times
        self.speed, self.vols_ = speed(times, vols)

        self.vols_line = Line3.from_coords(self.master, self.times, self.vols)
        self.speed_line = Line3.from_coords(self.master, self.vols_, self.speed)



def test_():
    root = Tk()
    tw = TextWindow(root)
    tw.mainloop()


if __name__ == '__main__':
    Container().mainloop()
    # test_()
