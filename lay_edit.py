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
import glob
import yaml
from multiprocessing import Process
from sys import version_info

from tkinter import *
import tkinter.ttk
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from tkinter.simpledialog import askfloat
from tkinter.messagebox import showinfo, askyesno, showerror

import compoz_read as cord

import cfg

mat_dir = cfg.val.dirmat


def xrun(modname, args):
    print(modname)  # run in a new process
    module = __import__(modname)  # build gui from scratch
    module.main(args)


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
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onExit)
        self._n = cfg.val.nrlay
        self._mat = '.' + cfg.val.extmat
        self._db = db.copy()
        if len(self._db.get('mat', '')) < 5:
            self._msd = os.path.join(os.path.dirname(__file__), mat_dir)
            self.lsdir()
        else:
            self._msd = self._db['mat']
            self.lsdir0()

        self._nmat = [' ' for id in range(self._n)]
        self._exist_mat = [False for id in range(self._n)]
        self._evp = [' ' for id in range(self._n)]
        self._rom = [' ' for id in range(self._n)]
        self._var = [StringVar() for id in range(self._n)]
        self._pv = [StringVar() for id in range(self._n)]
        self._ro = [StringVar() for id in range(self._n)]

        self.initUI()

        self.initdata()

        if len(self._db.get('lay', '')) > 5:
            self.onInit(self._db['lay'])
            self.parent.title(self._db['lay'])
            self._msf = self._db['lay']

    ##        self._sp = self.lsdir0()
    ##        self.onInit()

    def initUI(self):

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = Menu(menubar, tearoff=0)

        ##        fileMenu.add_command(label="Открыть слои РЭМП", underline=0,
        ##            command=(lambda i=False: self.onOpen(bpch=i)))
        ##        fileMenu.add_command(label="Открыть", underline=0, command=self.onOpen)
        ##        fileMenu.add_command(label="Создать", underline=0, command=self.initdata)
        fileMenu.add_command(label="Сохранить", underline=0, command=self.onSave)
        ##        fileMenu.add_command(label="Сохранить как", underline=0, command=self.onSaveAs)
        ##        fileMenu.add_command(label="mat-файлы", underline=0, command=self.lsdir)
        fileMenu.add_command(label="Выйти", underline=0, command=self.onExit)
        menubar.add_cascade(label="Файл", underline=0, menu=fileMenu)
        menubar.add_command(label="Помощь", underline=0, command=self.help)
        i = 0
        Label(self.parent, text='Материал', width=15).grid(row=0, column=0)
        Label(self.parent, text='Плотность гр/см\u00b3').grid(row=0, column=1)
        Label(self.parent, text='Номера слоёв').grid(row=0, column=2)
        ##        Entry(self.parent, text='Номера слоёв').grid(row=0, column=3)
        for i in range(self._n):
            ##            self._var[i].set('')
            ##            self._ro[i].set(-1.0)
            self._nmat[i] = Button(self.parent, text=self._var[i].get(), command=(lambda i=i: self.onEntry(i)))
            self._nmat[i].bind('<Button-2>', self.onEditMat)
            self._nmat[i].bind('<Button-3>', self.onInfo)
            self._nmat[i].grid(row=i + 1, column=0, padx=1, pady=1, sticky=W + E)

            self._rom[i] = Entry(self.parent, textvariable=self._ro[i], relief=SUNKEN,
                                 borderwidth=3, justify=RIGHT, width=5, state='disabled')
            self._rom[i].grid(row=i + 1, column=1, padx=1, pady=1, sticky=W + E)
            ##            self._pv[i].set([])
            self._evp[i] = Entry(self.parent, textvariable=self._pv[i], relief=GROOVE,
                                 borderwidth=3, justify=RIGHT, width=45)
            self._evp[i].grid(row=i + 1, column=2, padx=1, pady=1, sticky=W + E)
        pass

    def help(self):
        hlep = """
Для удаления материала, надо установить плотность равную нулю.
"""
        a = Toplevel()
        x = (self.parent.winfo_screenwidth() - self.parent.winfo_reqwidth()) / 2
        y = (self.parent.winfo_screenheight() - self.parent.winfo_reqheight()) / 2
        a.geometry("+%d+%d" % (x, y))

        ##        a.geometry('+{}+{}'.format(300, 250))
        ##        a['bg'] = 'grey'
        ##        a.overrideredirect(True)
        Button(a, text=hlep, command=lambda: a.destroy()).pack(expand=1)
        pass

    def initdata(self):
        for i in range(self._n):
            self._pv[i].set([0])
            self._var[i].set('_')
            self._ro[i].set(0.0)
            self._nmat[i]['text'] = self._var[i].get()

    def onInit(self, pth):
        ##        nmf = flname = askopenfilename(initialdir=os.getcwd(), title = u"Выберите материал",
        ##                        filetypes = [('layers','.*')] )
        ##        nmf = os.path.join(sd, 'layers0')
        d = cord.read_layer(os.path.dirname(pth), os.path.basename(pth))
        ##        print(self._sp)
        for i, ky in enumerate(sorted(d.keys())):
            nf = ky[0].lower()
            self._var[i].set(nf)
            if nf in self._sp:
                self._nmat[i]['fg'] = '#080'
                self._exist_mat[i] = True
            else:
                self._nmat[i]['fg'] = '#800'

            self._ro[i].set(ky[1])
            self._pv[i].set(d[ky])
            ##             print(self._nmat[i]['text'])
            self._nmat[i]['text'] = self._var[i].get()
        pass

    def onEditMat(self, event):
        nm = event.widget['text']

        if nm in self._sp:
            ##            return
            dp = {'file': os.path.join(self._msd, nm + '.' + cfg.val.extmat)}
            print(dp)
        else:
            dp = {'mat': self._msd, 'name': nm.upper()}
        import edit_mat as em
        ta = Toplevel()
        ##            tm.title(nm + self._mat)
        ta.resizable(False, False)
        ta.geometry("+%d+%d" % (event.x_root, event.y_root))
        ex = em.Example(ta, dp)
        ta.grab_set()
        ta.focus_set()
        ta.wait_window()
        event.widget['fg'] = '#00f'
        self.onInfo(event)

    def onEditMatOld(self, event):
        nm = event.widget['text']
        if nm in self._sp:
            return
        dp = {'mat': self._msd, 'name': nm.upper()}
        Process(target=xrun, args=('edit_mat', dp)).start()
        pass

    def xxonEditMat(self, event):
        from . import edit_mat as em

        nm = event.widget['text']
        if nm in self._sp:
            return
        dp = {'mat': self._msd, 'name': nm.upper()}
        tm = Toplevel()
        tm.title(nm + self._mat)
        tm.resizable(False, False)
        tm.geometry("+%d+%d" % (event.x_root, event.y_root))
        ex = em.Example(tm, dp)

    ##        tm.grab_set()
    ##        tm.focus_set()
    ##        tm.wait_window()

    def call(self, position):
        pass

    ##        print([self._var[i].get() for i in range(self._n)])

    def onEntry(self, val):
        flnm = askopenfilename(initialdir=self._msd, title="Выберите материал",
                               filetypes=[('Mat file', self._mat)])
        ##        print(flnm)
        if len(flnm) > 5:
            tt = os.path.split(flnm)[1]
            nm = os.path.splitext(tt)[0]
            self._var[val].set(nm)
            self._nmat[val]['text'] = self._var[val].get()
            self._nmat[val]['fg'] = '#080'
            self._exist_mat[val] = True

    def onExit(self):
        answer = askyesno(title="Сохранение файла", message="Сохранить файл?")
        if answer == True:
            check = self.onSave()
            if check == 0:
                self.parent.destroy()
            else:
                ask = askyesno('Mat files','Мат файлы не выбраны.\nВыбрать мат файлы?\n нет - программа будет закрыта')
                if ask is True:
                    return
                else:
                    self.parent.destroy()
        elif answer == False:
            self.parent.destroy()

    def onSave(self):
        """ """
        sps = []
        for i in range(self._n):
            if len(self._ro[i].get()) == 0 or self._nmat[i]['text'] == '_':
                continue
            if self._exist_mat[i] is False:
                showerror('Mat error','Выбраны не все мат файлы')
                return 1
            ro = float(self._ro[i].get())
            if ro > 0.0:
                nmat = self._var[i].get()
                ls = self._pv[i].get()
                ls = ls.replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace(
                    '}', '')
                ls = ls.replace(',', '').replace('.', '').replace(';', '').replace(':', '')
                ##                ls = ls.replace(']','')
                tt = (ls.split())
                for k in tt:
                    sps.append([int(k), nmat, ro])
        ##        print(msd)
        with open(self._db['lay'], 'w') as ff:
            for ls in sps:
                ##                print(ls)
                ff.write('{0:d}\t{1:s}\t{2:f}\n'.format(ls[0], ls[1], ls[2]))

        self.initdata()

        if len(self._db.get('lay', '')) > 5:
            self.onInit(self._db['lay'])
            self.parent.title(self._db['lay'])
            self._msf = self._db['lay']

        return 0

    def onSaveAs(self):
        """ """
        msd = asksaveasfilename(initialdir=os.path.dirname(self._db['lay']), initialfile=self._db['lay'],
                                title="Куда сохраните файл")
        if len(msd) < 5:
            return
        sps = []
        for i in range(self._n):
            if len(self._ro[i].get()) == 0:
                continue
            ro = float(self._ro[i].get())
            if ro > 0.0:
                nmat = self._var[i].get()
                ls = self._pv[i].get()
                ls = ls.replace('[', '')
                ls = ls.replace(']', '')
                tt = (ls.split(','))
                for k in tt:
                    sps.append([int(k), nmat, ro])
        print(msd)
        with open(os.path.join(os.path.normpath(msd)), 'w') as ff:
            for ls in sps:
                ##                print(ls)
                ff.write('{0:d}\t{1:s}\t{2:f}\n'.format(ls[0], ls[1], ls[2]))

    def onOpen(self, bpch=True):
        """
        """
        if bpch:
            sft = ('Оболочки layers', '.*')
            flnm = self._db['lay']
        else:
            sft = 'Слои РЭМП', '.LTB'
            flnm = self._db['rmp']

        ##        print(self._msf)
        flnm = askopenfilename(initialdir=os.path.dirname(self._msf), title="Выберите файл со слоями",
                               initialfile=flnm, filetypes=[sft])
        if len(flnm) > 5:
            self._msf = flnm
            ##            print(self._msf)
            self.parent.title(self._msf)
            d = cord.read_layer(flnm, nmfl='')
            self.initdata()
            for i, ky in enumerate(sorted(d.keys())):
                nf = ky[0].lower()
                if nf in self._sp:
                    self._nmat[i]['fg'] = '#080'
                    self._exist_mat[i] = True
                else:
                    self._nmat[i]['fg'] = '#800'
                self._var[i].set(nf)
                self._ro[i].set(ky[1])
                self._pv[i].set(d[ky])

                self._nmat[i]['text'] = self._var[i].get()
        pass

    def onInfo(self, event):
        """ """
        nm = event.widget['text']
        if len(nm) > 0 and nm != '_':
            nmfl = os.path.join(self._msd, nm + self._mat)
            xinf = self._msd + '\n'
            bb = {}
            tt = cord.read_mat(nmfl, mess=bb)
            msg = bb.get('mes', '')
            ta = Toplevel()
            ta.title(nm + self._mat)
            ta.resizable(False, False)
            ta.geometry("+%d+%d" % (event.x_root, event.y_root))
            bt = Button(ta, text='', command=lambda: ta.destroy())
            if len(msg) == 0:
                xinf += cord.dump_mat(tt)
                bt['fg'] = '#080'
                event.widget['fg'] = '#080'
            else:
                xinf += msg
                bt['fg'] = '#800'
                event.widget['fg'] = '#800'
            bt['text'] = xinf
            bt.pack(expand=1)
            ta.grab_set()
            ta.focus_set()
            ta.wait_window()

    def lsdir(self):
        self._msd = askdirectory(initialdir=self._msd, title="Выберите директорию с mat файлами")
        ##        msd='c:\\projects\\python\\Material\\mat-files'
        ##        print(msd)
        allmat = glob.glob(os.path.normpath(self._msd) + os.sep + '*' + self._mat)
        tt = [os.path.split(ff)[1] for ff in allmat]
        self._sp = [os.path.splitext(ff)[0] for ff in tt]

    def lsdir0(self):
        allmat = glob.glob(os.path.normpath(self._msd) + os.sep + '*' + self._mat)
        tt = [os.path.split(ff)[1] for ff in allmat]
        self._sp = [os.path.splitext(ff)[0] for ff in tt]


def main(db):
    ##    sd = os.getcwd()
    ##    (na, nu) = cor.read_elements(sd)
    er = Tk()
    ex = Example(er, db)
    x = (er.winfo_screenwidth() - er.winfo_reqwidth()) / 2
    y = (er.winfo_screenheight() - er.winfo_reqheight()) / 4
    er.geometry("+%d+%d" % (x, y))
    er.mainloop()


if __name__ == '__main__':
    dp = {}
    flnm = os.path.join(os.path.dirname(__file__), 'config.yml')
    try:
        dp = yaml.load(open(flnm, 'rt'))
    except:
        pass
    main(dp)
    pass
