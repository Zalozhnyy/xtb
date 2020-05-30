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
import numpy as np
import glob
import yaml

from sys import version_info

v = version_info[0]
if v == 3:
    from tkinter import *
    from tkinter.filedialog import askopenfilename, askdirectory
    from tkinter.simpledialog import askfloat
else:
    from tkinter import *
    from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
    from tkinter.simpledialog import askfloat
    from tkinter.messagebox import showinfo

import compoz_read as cord

mat_dir = 'mat-files'


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
    def __init__(self, parent, db):

        Frame.__init__(self, parent)
        self._parent = parent
        ##        print(db)
        self.xin = {}
        self._flpar = StringVar(None, '')
        self._db = db
        if len(list(db.keys())) == 0:
            path = os.path.dirname(__file__)
            flnm = 'parameters.ini'

        else:
            flnm = db['par']
            path = os.path.split(flnm)[0]
            flnm = os.path.split(flnm)[1]
        self._msf = os.path.join(path, flnm)
        self._flpar.set(os.path.normpath(self._msf))
        self.read_param(nExePath=path, nFile=flnm)
        self._parent.title(self._flpar.get())

        self._sp = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 50, 100]

        self._var = [IntVar() for id in self._xKey]

        self.initUI()

    def initUI(self):

        menubar = Menu(self._parent)
        self._parent.config(menu=menubar)

        fileMenu = Menu(menubar, tearoff=0)

        fileMenu.add_command(label="Открыть", underline=0, command=self.onOpen)
        fileMenu.add_command(label="Сохранить", underline=0, command=self.onSave)
        fileMenu.add_command(label="Сохранить как", underline=0, command=self.onSaveAs)

        ##        fileMenu.add_command(label="mat-файлы", underline=0, command=self.lsdir)
        fileMenu.add_command(label="Выйти", underline=0, command=self.onExit)
        menubar.add_cascade(label="Файл", underline=0, menu=fileMenu)
        menubar.add_command(label="Помощь", underline=0, command=self.about)
        i = 0
        frame_par = LabelFrame(self._parent, bd=1, text='Параметры выходных таблиц')
        frame_par.pack(fill=BOTH, expand=True, padx=15, pady=10)

        Label(frame_par, text='Параметр', width=20).grid(row=0, column=0, padx=1, pady=1, sticky=E)
        Label(frame_par, text='Значение', width=8).grid(row=0, column=1)
        self._lnm = []
        self._lev = []
        k = 1
        for i, key in enumerate(self._xKey):
            evp = Label(frame_par, text=key, relief=GROOVE,
                        borderwidth=3, justify=RIGHT, width=20,
                        ).grid(row=i + k, column=0,
                               padx=1, pady=1, sticky=E)
            self._lev.append(evp)
            ##            print(self.xin[key]['n'])
            self._var[i].set(self.xin[key]['n'])
            nm = OptionMenu(frame_par, self._var[i], *self._sp,
                            command=self.call).grid(row=i + k, column=1, padx=1, pady=1, sticky=W + E)
            self._lnm.append(nm)
            pass

    def call(self, position):
        pass

    ##        print('pos {0} '.format(position))
    ##        print([(id.get()) for id in self._var])
    ##        print(self._var[position].get())

    def onEntry(self, val):
        v = int(float(val))
        self._evr.set(v)

    def onExit(self):
        self.quit()

    def sum(self):
        ##        tt = [float(self._pv[i].get()) for i in range(self._n)]
        ##        showinfo('Сумма массовых долей', str(sum(tt)))
        pass

    def about(self):
        hlep = """
Сетка по энергии строится по следующей формуле:
    Количество точек по энергии определяется nE=(En*(Emax-Emin)+1) и
    равномерная сетка E по десятичному логарифму от [Emin] до [Emax] с
    количеством узлов nE.
    Тогда шаг сетки будет равен (Emax - Emin)/(nE - 1). Сетка будет равна 10^E.
"""
        a = Toplevel()
        x = (self._parent.winfo_screenwidth() - self._parent.winfo_reqwidth()) / 2
        y = (self._parent.winfo_screenheight() - self._parent.winfo_reqheight()) / 2
        a.geometry("+%d+%d" % (x, y))

        ##        a.geometry('+{}+{}'.format(300, 250))
        ##        a['bg'] = 'grey'
        ##        a.overrideredirect(True)
        Button(a, text=hlep, command=lambda: a.destroy()).pack(expand=1)

    ##        a.after(5000, lambda: a.destroy())

    def onSaveAs(self):
        """ """
        sps = {}
        for i, key in enumerate(self._xKey):
            sps[key] = self._var[i].get()

        msf = asksaveasfilename(initialdir=os.path.dirname(self._msf), initialfile=self._msf,
                                title="Куда сохраните файл",
                                filetypes=[('Параметр файл', '.ini')])
        if len(msf) > 1:
            ##            with open(msf,'w') as ff:
            ##                ff.write(yaml.dump(sps, default_flow_style = False,))
            with open(msf, 'w') as ff:
                for key in self._xKey:
                    ff.write('[{0:s}]\t{1:d}\n'.format(key, int(sps[key])))

            self._db['par'] = os.path.normpath(msf)
            self._msf = self._db['par']

    def onSave(self):
        """ """
        sps = {}
        for i, key in enumerate(self._xKey):
            sps[key] = self._var[i].get()

        ##        msf = asksaveasfilename(initialdir=os.getcwd(),  initialfile='parameters.ini', title = u"Куда сохраните файл",
        ##                        filetypes = [('Параметр файл','.ini')])
        ##        if len(msf) > 1:
        ##            with open(msf,'w') as ff:
        ##                ff.write(yaml.dump(sps, default_flow_style = False,))
        with open(self._msf, 'w') as ff:
            for key in self._xKey:
                ff.write('[{0:s}]\t{1:d}\n'.format(key, int(sps[key])))

    def onOpen(self):
        msf = askopenfilename(initialdir=os.path.split(self._flpar.get())[0], title="Выберите параметры",
                              filetypes=[('Параметр файл', '.ini')])

        if len(msf) > 1:
            self._flpar.set(os.path.normpath(msf))
            self.read_param(nExePath=os.path.split(self._flpar.get())[0],
                            nFile=os.path.split(self._flpar.get())[1])
            self._parent.title(self._flpar.get())
            ##            print(msf)
            ##            print(self.xin)
            for i, key in enumerate(self._xKey):
                self._var[i].set(self.xin[key]['n'])

        pass

    def read_param(self, nExePath='', nFile=''):
        """
        """
        ##        self.xin= {}
        ##        self.Z =Z #number element
        if len(nExePath) == 0:
            nExePath = os.path.dirname(__file__)
        self._xKey = ['Emin', 'Emax', 'En', 'nG', 'nG_el', 'nG_ion', 'nG_br', 'nG_br_tet',
                      'nG_photo', 'nG_para', 'nG_annig']
        ##        self.xin['Emin'] = 2.0
        ##        self.xin['Emax'] = 7.0
        ##        self.xin['En'] = 5
        nn = 10

        import math
        ##        self.xin['nG'] = int(math.pow(2,nn)) # for photons
        ##        self.xin['nX'] = int(math.pow(2,nn)) # for photons
        ##        self.xin['nG_el'] = int(math.pow(2,nn)) # for electrons
        ##        self.xin['nG_ion'] = int(math.pow(2,nn))
        ##        self.xin['nG_br'] = int(math.pow(2,6))
        ##        self.xin['nG_para'] = int(math.pow(2,nn))

        nf = nFile if len(nFile) > 0 else 'parameter.ini'
        nFile = os.path.join(nExePath, nf)
        ##        print(nFile)
        try:
            with open(nFile, 'r') as fIn:
                for k, line in enumerate(fIn):
                    t = line.split()
                    if line.startswith('[n'):
                        kl = t[0][1:-1]
                        tt = int(t[1])
                        self.xin[kl] = {'n': tt, 'v': int(math.pow(2, tt))}
                    elif line.startswith('[E'):
                        kl = t[0][1:-1]
                        tt = int(t[1])
                        ##                        print(tt)
                        self.xin[kl] = {'n': tt}
        ##                print(self.xin)
        except IOError:
            print(('Oтсутствует файл {0}. Используются значения по умолчанию.'.format(nFile)))


##        self.xin['nE'] = {'v': int(self.xin['En']['n']*(self.xin['Emax']['n'] -
##                        self.xin['Emin']['n'])+1)}


def main(db):
    ##    sd = os.getcwd()
    ##    (na, nu) = cor.read_elements(sd)
    root = Toplevel()
    ex = Example(root, db)
    ##    root.geometry("250x550+300+50")
    #root.mainloop()


if __name__ == '__main__':
    """ """
    db = {}
    main(db)
    pass
