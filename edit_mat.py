# -*- coding: utf-8 -*-
# !/usr/bin/env python
# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Сергей
#
# Created:     18.11.2018
# Copyright:   (c) Сергей 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import os
##import numpy as np
import yaml

from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter.simpledialog import askfloat
from tkinter.messagebox import showinfo, askyesno

import compoz_read as cor

import cfg

mat_dir = cfg.val.dirmat


def min0ne(f):
    def tmp(*args, **kwargs):
        res = f(*args, **kwargs)

        return res[0] - 1, res[1] - 1

    return tmp


@min0ne
def z2rc(Z_):
    """
    """
    endCol_ = 18

    if Z_ == 1:
        return (1, 1)
    if Z_ == 2:
        return (1, endCol_)

    if Z_ in (3, 4):
        return (2, 1 + Z_ - 3)
    if Z_ in range(5, 11):
        return (2, 8 + Z_)

    if Z_ in (11, 12):
        return (3, 1 + Z_ - 11)
    if Z_ in range(13, 19):
        return (3, Z_)

    if Z_ in range(19, 37):
        return (4, 1 + Z_ - 19)
    if Z_ in range(37, 55):
        return (5, 1 + Z_ - 37)

    if Z_ in (55, 56, 57):
        return (6, 1 + Z_ - 55)
    if Z_ in range(72, 87):
        return (6, 4 + Z_ - 72)

    if Z_ in (87, 88, 89):
        return (7, 1 + Z_ - 87)
    if Z_ in range(104, 115):
        return (7, 4 + Z_ - 104)

    if Z_ in range(58, 72):
        return (8, 4 + Z_ - 58)
    if Z_ in range(90, 104):
        return (9, 4 + Z_ - 90)
    return (0, 0)

    """   """


def fixWindowsPath(cmdline):
    """
    change all / to \ in script filename path at front of cmdline;
    used only by classes which run tools that require this on Windows;
    on other platforms, this does not hurt (e.g., os.system on Unix);
    """
    splitline = cmdline.lstrip().split(' ')  # split on spaces
    fixedpath = os.path.normpath(splitline[0])  # fix forward slashes
    return ' '.join([fixedpath] + splitline[1:])  # put it back together


class Example(Frame):
    """ """

    def __init__(self, parent, db):
        Frame.__init__(self, parent)
        if len(db.get('mat', '')) < 5:
            self._msd = os.path.join(os.path.dirname(__file__), mat_dir)
        else:
            self._msd = db['mat']
        self._bion = False
        self._lion = []
        self._vion = BooleanVar()
        self._vion.set(self._bion)
        self._parent = parent
        self._parent.protocol("WM_DELETE_WINDOW", self.onExit)
        sd = os.path.dirname(__file__)
        (na, nu) = cor.read_elements(sd)
        self._nu = nu
        self._sp = sorted(nu.keys())
        self._n = cfg.val.nrmat
        self._mat = '.' + cfg.val.extmat
        self._nmat = [' ' for id in range(self._n)]
        self._bmat = []
        self._sp = [0, 1, 2]
        self._ent = [' ' for id in range(self._n)]
        self._bt = [' ' for id in range(self._n)]
        self._var = [StringVar(master=parent) for id in range(self._n)]
        self._veion = [StringVar(master=parent) for id in range(self._n)]
        self._pv = [StringVar(master=parent) for id in range(self._n)]
        self._name_mt = StringVar(parent, db.get('name', 'MATERIAL'))
        self._ro = StringVar(parent)
        self._ro.set(1.0)
        self._nelm = 100
        self._dmt = self.read_elements()[0]
        self.initMenu()
        self.initUI()
        flnm = db.get('file', '')
        if len(flnm) > 5:
            if '+' in flnm:
                self._bion = True
                self.showIon()
            else:
                self._bion = False
                self.hideIon()
            self._vion.set(self._bion)
            self.initdata()
            ms = cor.Compozit(flnm, self._nu)
            self._name_mt.set(ms._vv[0][0]['Composite'])
            self._ro.set(ms._vv[0][0]['Density'])
            for i, mt in enumerate(ms._vv[0][0]['Element']):
                self._var[i].set(mt[0])
                self._bt[i]['text'] = mt[0]
                self._pv[i].set(mt[1])
                self._veion[i].set(mt[2])

    def initMenu(self):
        self._parent.title("Композиты")

        menubar = Menu(self._parent)
        self._parent.config(menu=menubar)

        fileMenu = Menu(menubar, tearoff=0)

        fileMenu.add_command(label="Открыть", underline=0, command=self.onOpen)
        fileMenu.add_command(label="Создать", underline=0, command=self.initdata)
        fileMenu.add_command(label="Сохранить", underline=0, command=self.onSave)
        #fileMenu.add_command(label="Сохранить как", underline=0, command=self.onSaveAs)
        fileMenu.add_separator()
        fileMenu.add_command(label="Проверить", underline=0, command=self.suminfo)
        fileMenu.add_separator()
        fileMenu.add_command(label="Выйти", underline=0, command=self.onExit)
        menubar.add_cascade(label="Файл", underline=0, menu=fileMenu)

        fileServ = Menu(menubar, tearoff=0)
        fileServ.add_checkbutton(label="Ионизированный", variable=self._vion,
                                 underline=0, command=self.onIon)

        menubar.add_cascade(label="Сервис", underline=0, menu=fileServ)


    def initUI(self):

        frame_ = Frame(self._parent, bd=1)
        frame_.pack(fill=BOTH, expand=True, padx=10)
        i = 0
        bo = Button(frame_, text='Открыть', command=self.onOpen, relief=RAISED).grid(row=i,
                                                                                     column=0, padx=5, pady=10,
                                                                                     sticky=W + E)
        bm = Button(frame_, text='Создать', command=self.initdata, relief=RAISED).grid(row=i,
                                                                                       column=1, padx=5, pady=10,
                                                                                       sticky=W + E)
        i += 1
        Label(frame_, text='Наименование').grid(row=i, column=0)
        self._name_comp = Entry(frame_, textvariable=self._name_mt, relief=SUNKEN,
                     justify=RIGHT)
        self._name_comp.bind('<FocusOut>', self.tblIon)
        self._name_comp.grid(row=i, column=1, padx=1, ipady=0, pady=0, sticky=W + E)
        i += 1
        # Label(frame_, text='Плотность').grid(row=i, column=0)
        # ro = Entry(frame_, textvariable=self._ro, relief=SUNKEN, state='disabled',
        #            justify=RIGHT).grid(row=i, column=1, padx=0, ipady=0, pady=1, sticky=W + E)
        # i += 1
        Label(frame_, text='Хим. элемент').grid(row=i, column=0)
        Label(frame_, text='Массовая Доля').grid(row=i, column=1)

        self._lab_ion = Label(frame_, text='Заряд Иона', width=10)
        self._lab_ion.grid(row=i, column=2)

        k = i + 1

        for i in range(self._n):
            self._bt[i] = Button(frame_, text='  ', relief=GROOVE)
            self._bt[i].bind('<Button-1>', self.tblMendel)
            self._bt[i].bind('<Delete>', self.delMendel)
            self._bt[i].grid(row=i + k, column=0, padx=5, pady=1, sticky=W + E)
            self._pv[i].set(0.0)
            self._ent[i] = Entry(frame_, textvariable=self._pv[i], relief=SUNKEN,
                                 justify=RIGHT)
            self._ent[i].grid(row=i + k, column=1, padx=5, pady=1, sticky=W + E)
            ##            self._bmat.append(bt)

            ##            ni = Spinbox(frame_, values=(0, 1, 2), width=5, bg='#FFFFFF', fg='#000000')
            self._veion[i].set(0)
            ni = OptionMenu(frame_, self._veion[i], *self._sp)

            ni.grid(row=i + k, column=2, padx=5, pady=1, sticky=W + E)
            self._lion.append(ni)
            pass
            ##        if not self._bion:
            ##            self._lab_ion.grid_remove()

        if not self._bion:
            self._lab_ion.grid_remove()
            for i in range(self._n):
                self._lion[i].grid_remove()

        bs = Button(frame_, text='Сохранить', command=self.onSave, relief=RAISED).grid(row=i + k,
                                                                                       column=0, columnspan=2, padx=5,
                                                                                       pady=10, sticky=W + E)

    def call(self, position):
        pass

        ##        print([self._var[i].get() for i in range(self._n)])

    def callbk(self, event):
        print(event.widget)

    def tblIon(self, event):

        if '+' in self._name_mt.get():
            self._bion = True
            self.showIon()
        else:
            self._bion = False
            self.hideIon()
        self._vion.set(self._bion)

    def onIon(self):
        if '+' in self._name_mt.get():
            self._bion = True
            self.showIon()
            self._vion.set(self._bion)
            return

        self._bion = self._vion.get()
        self._vion.set(self._bion)
        if self._bion:
            self.showIon()
        ##            for i in range(self._n):
        ##                self._lion[i].grid()
        ##            self._lab_ion.grid()
        else:
            self.hideIon()

    ##            for i in range(self._n):
    ##                self._lion[i].grid_remove()
    ##             self._lab_ion.grid_remove()

    def showIon(self):
        self._lab_ion.grid()
        for i in range(self._n):
            self._lion[i].grid()

    def hideIon(self):
        for i in range(self._n):
            self._lion[i].grid_remove()
        self._lab_ion.grid_remove()

    def initdata(self):
        self._name_mt.set('MATERIAL')
        self._ro.set(0.0)
        for i in range(self._n):
            self._pv[i].set(0.0)
            self._bt[i]['text'] = ''

    def elem(self, k, event):
        self._k = k
        ##        print(' k %d'%k)
        event.widget['text'] = self._dmt[k]['name']
        self._ta.destroy()

    def tblMendel(self, event):
        self._ta = Toplevel()
        self._ta.geometry("+%d+%d" % (event.x_root, event.y_root))
        self._ta.title("Таблица Менделеева")

        lb = []
        for k in range(1, self._nelm):
            i, j = z2rc(k)
            b = Button(self._ta, text=str(k) + ':' + self._dmt[k]['name'], relief=RIDGE,
                       command=(lambda k=k: self.elem(k, event)))
            b.grid(row=i, column=j, sticky=NSEW)
            if event.widget['text'] == self._dmt[k]['name']:
                b['fg'] = '#00f'
            ##            b.bind("<Button-1>", self.callbk)
            lb.append(b)
        ##        print(self._k)
        self._ta.grab_set()
        self._ta.focus_set()
        self._ta.wait_window()

    def delMendel(self, event):
        event.widget['text'] = ''

    def onEntry(self, val):
        v = int(float(val))
        self._evr.set(v)

    def onExit(self):
        answer = askyesno(title="Сохранение файла", message="Сохранить файл?")
        if answer == True:
            bt = self.onSave()
            self._parent.destroy()
        else:
            self._parent.destroy()

    def sum(self):
        tt = [float(self._pv[i].get()) for i in range(self._n) if len(self._bt[i]['text']) > 0]
        sm = sum(tt)
        return sm

    def suminfo(self):
        sm = self.sum()
        showinfo('Сумма массовых долей', str(sm))

    def sum_rkt(self):
        sm = self.sum()
        if abs(1.0 - sm) <1.e-5:
            return True
        else:
            showinfo('Сумма массовых долей', str(sm))
            return False

    # def onSaveAs(self):
    #     name = self._name_mt.get()
    #     name = name.lower()
    #     mt = {}
    #     sps = []
    #     tt = [float(self._pv[i].get()) for i in range(self._n)]
    #     for i, pp in enumerate(tt):
    #         if pp > 0.0:
    #             ##                sps.append([self._var[i].get(), pp])
    #             sps.append([self._bt[i]['text'], pp])
    #
    #     mt[name.upper()] = {'elem': sps, 'ro': float(self._ro.get())}
    #     ##        msd = askdirectory(initialdir=self._msd, title = u"Куда сохраните файл")
    #     msf = os.path.join(fixWindowsPath(self._msd), name + self._mat)
    #     msf = asksaveasfilename(initialdir=self._msd, initialfile=msf, title="Сохраняем файл")
    #     if len(msf) > 1:
    #         cor.write_file(msf, mt)

    ##        print(msd)
    ##        with open(os.path.join(fixWindowsPath(msd), name + '.yml'),'w') as ff:
    ##            ff.write(yaml.dump(mt))
    ##        self._msd = msd

    def onSave(self):
        if not self.sum_rkt():
            return  False
        name = self._name_mt.get()
        name = name.lower()
        mt = {}
        sps = []
        tt = [float(self._pv[i].get()) for i in range(self._n)]
        for i, pp in enumerate(tt):
            if pp > 0.0:
                nms = self._bt[i]['text']
                print(nms)
                ##                if self._bion:
                if len(nms) > 0:
                    cion = int(self._veion[i].get())
                    print(cion)
                    if cion > 0:
                        sps.append([nms, pp, cion])
                    else:
                        sps.append([nms, pp])

        mt[name.upper()] = {'elem': sps, 'ro': float(self._ro.get())}
        ##        msd = askdirectory(initialdir=self._msd, title = u"Куда сохраните файл")
        msf = os.path.join(fixWindowsPath(self._msd), name + self._mat)
        ##        msf = asksaveasfilename(initialdir=self._msd, initialfile=msf, title = u"Сохраняем файл")
        if len(msf) > 1:
            print(mt)
            cor.write_file(msf, mt)

    ##        print(msd)
    ##        with open(os.path.join(fixWindowsPath(msd), name + '.yml'),'w') as ff:
    ##            ff.write(yaml.dump(mt))
    ##        self._msd = msd

    def onOpen(self):
        flnm = askopenfilename(initialdir=self._msd, title="Выберите материал",
                               filetypes=[('Mat file', self._mat)])
        if len(flnm) > 5:
            if '+' in flnm:
                self._bion = True
                self.showIon()
            else:
                self._bion = False
                self.hideIon()
            self.initdata()
            ms = cor.Compozit(flnm, self._nu)
            print('read mat')
            self._name_mt.set(ms._vv[0][0]['Composite'])
            self._ro.set(ms._vv[0][0]['Density'])
            for i, mt in enumerate(ms._vv[0][0]['Element']):
                self._var[i].set(mt[0])
                self._bt[i]['text'] = mt[0]
                self._pv[i].set(mt[1])
                self._veion[i].set(mt[2])

        pass

    def read_elements(self):
        import csv
        elm = {}
        eln = {}
        with open(os.path.join(os.path.dirname(__file__), 'elements.csv'), "r") as flf:
            rr = csv.DictReader(flf, delimiter='\t')
            for rw in rr:
                elm[rw['El']] = {'NN': int(rw['NN']), 'Ro': rw['Ro'], 'A': rw['A']}
                eln[int(rw['NN'])] = {'name': rw['El'], 'Ro': rw['Ro'], 'A': rw['A']}

            pass

        return (eln, elm)


def main(db):
    er = Toplevel()
    ex = Example(er, db)
    x = (er.winfo_screenwidth() - er.winfo_reqwidth()) / 2
    y = (er.winfo_screenheight() - er.winfo_reqheight()) / 4
    er.geometry("+%d+%d" % (x, y))
    #er.mainloop()


if __name__ == '__main__':

    dp = {}
    flnm = os.path.join(os.path.dirname(__file__), 'config.yml')
    try:
        dp = yaml.load(open(flnm, 'rt'))
    except:
        pass
    main(dp)
