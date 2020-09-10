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
import sys
import os

sys.path.append(os.path.dirname(__file__))
# __file__ = os.path.join('..//share//scripts//xtb//', 'tables.py')

import os
import json
# import glob
import shutil
import yaml

from multiprocessing import set_executable
from multiprocessing.dummy import Process
# from multiprocessing import Process
import logging

from sys import version_info

v = version_info[0]
import locale
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
import tkinter.filedialog as fd
from tkinter.simpledialog import askfloat
from tkinter import messagebox

from calc_tables import main as main_calc_tables

##from make_constant import make_const
##from calculate import monte_carlo
##from read_proj import read_prj
##import edit_mat
import param
import cfg
from Project_reader_tables import DataParcer


def read_prj(prjfname, stk='Layers name'):
    """
    """
    reads = True
    sname = ""
    try:
        with open(prjfname) as prjf:
            lfn = prjf.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % prjfname))
    ##        exit(-1)
    readgrd = True
    grdfname = ""
    readcll = True
    cllfname = ""
    i = 0
    while (reads):
        if lfn[i].find(stk) > 0:
            break
        i += 1
    i += 1
    sname = lfn[i].strip()
    return sname


def xxmkdir(drname):
    dirname = os.path.normpath(drname)
    print(os.getcwd())
    if not os.path.isdir(os.path.join(os.getcwd(), dirname)):
        os.makedirs(os.path.join(os.getcwd(), dirname))


def pech_open_dir(path):
    messagebox.showwarning('Path error', 'Не обнаружена папка проекта переноса.\n'
                                         'Выберите директорию переноса вручную')
    pech_path = fd.askdirectory(title='Выберите директорию проекта переноса',
                                initialdir=path)
    if pech_path == '':
        return -1
    if 'configuration' in os.listdir(pech_path):
        return os.path.abspath(pech_path)
    else:
        messagebox.showwarning('Path error', 'Папка не является проектом переноса (Не обнаружен файл configuration.)')
        ask = messagebox.askyesno('Выбрать другую папку?', 'Выбрать другую папку?')
        if ask is True:
            pech_open_dir(path)
        elif ask is False:
            return -1


def pech_ask(path):
    ask_pe = messagebox.askyesno('Проект переноса', 'В расчёте нужен проект переноса?.\n'
                                                 'да - указать путь к проекту переноса\n'
                                                 'нет - продолжить без проекта переноса')
    if ask_pe is True:
        pech_dir = pech_open_dir(path)
        if pech_dir == -1:
            return -1
        else:
            return pech_dir
    elif ask_pe is False:
        pech_dir = 'temp'
        if not os.path.exists(os.path.join(path, 'temp')):
            os.mkdir(os.path.join(path, 'temp'))
        return os.path.join(path, pech_dir)


def pech_existance(pr_path):
    path = os.path.abspath(pr_path)
    if any([i == 'pechs' for i in os.listdir(path)]):
        if 'configuration' in os.listdir(os.path.join(path, 'pechs')):
            return os.path.join(path, 'pechs')

    elif 'pechs.proj.addr' in os.listdir(path):
        file = os.path.join(pr_path, 'pechs.proj.addr')

        try:
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file, 'r', encoding=f'{locale.getpreferredencoding()}') as f:
                lines = f.readlines()

        pech_name = lines[0].strip()
        if os.path.exists(os.path.join(pr_path, pech_name)):
            if os.path.exists(os.path.join(os.path.join(pr_path, pech_name), 'configuration')):
                return os.path.join(pr_path, pech_name)
            else:
                pech_dir = pech_ask(path)
                if pech_dir == -1:
                    return -1
                else:
                    return os.path.normpath(pech_dir)
        else:
            pech_dir = pech_ask(path)
            if pech_dir == -1:
                return -1
            else:
                return os.path.normpath(pech_dir)
    elif True:
        pech_dir = pech_ask(path)
        return os.path.normpath(pech_dir)


def info(title):
    print(title)
    print('module name:', __name__)
    if hasattr(os, 'getppid'):  # only available on Unix
        print('parent process:', os.getppid())
    print('process id:', os.getpid())


def xrun(modname, args):
    ##    print(modname)                     # run in a new process
    # info(modname)
    module = __import__(modname)  # build gui from scratch
    if modname == 'lay_edit':
        module.main(args[0], args[1])
    else:
        module.main(args)


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self._parent = parent
        self._parent.protocol("WM_DELETE_WINDOW", self.onExit)
        self._vir = IntVar(None, 3)
        self._ro = 1.0
        self._vapel = BooleanVar()
        self._vapel.set(1)
        self._vapph = BooleanVar()
        self._vapph.set(1)
        self._evr = IntVar(None, 100)
        ##        self._flprj = StringVar(None, '')
        self._plc_tab = StringVar(None, '')
        self._flpar = StringVar(None, '')
        self._plc_prt = StringVar(None, '')
        self._flrmp = StringVar(None, '')
        self._fllay = StringVar(None, '')
        self._flcfg = StringVar(None, os.path.join(os.path.dirname(__file__), 'config.yml'))
        self._plc_mat = StringVar(None, os.path.normpath(os.path.join(os.path.dirname(__file__), cfg.val.dirmat)))
        self._kky = ['lay', 'tab', 'rmp']
        self._stbt = DISABLED
        ##        self._bd = {'electron': self._vapel.get(), 'photon': self._vapph.get()}

        ##        answ = messagebox.askyesno(title="Вопрос", message="Открыть конфигурационный файл проекта?")
        ##        if answ:
        ##            self.onOpenCfg()
        ##        else:
        ##            self.onConfig()
        self.initUI()

    def initUI(self):
        self._parent.title("Подготовка даных для вычисления распределений")
        menubar = Menu(self._parent)
        self._parent.config(menu=menubar)

        fileMenu = Menu(menubar, tearoff=0)

        fileMenu.add_command(label="Открыть Проект", underline=0, command=self.onConfig)
        fileMenu.add_command(label="Открыть конфигурацию", underline=0, command=self.onOpenCfg)

        ##        fileMenu.add_command(label="Открыть материалы", underline=0, command=self.onChoiceMat)
        fileMenu.add_command(label="Сохранить конфигурацию", underline=0, command=self.onSave)
        fileMenu.add_command(label="Выйти", underline=0, command=self.onExit)
        menubar.add_cascade(label="Файл", underline=0, menu=fileMenu)
        ##        distMenu = Menu(menubar, tearoff=0)
        ##        distMenu.add_command(label="Косинус угла(фотопоглощение)", underline=0, command=self.onElPhoto)
        ##        distMenu.add_command(label="Косинус угла тормозного фотона", underline=0, command=self.onPhBrems)
        ##        distMenu.add_command(label="Энергия позитрона", underline=0, command=self.onPhAnig)
        ##        menubar.add_cascade(label="Распределения Независимые", underline=0, menu=distMenu)
        servMenu = Menu(menubar, tearoff=0)
        servMenu.add_command(label="Графики", underline=0, command=self.onViewTable)
        servMenu.add_command(label="Параметры", underline=0, command=self.onEditPar)
        menubar.add_cascade(label="Сервис", underline=0, menu=servMenu)

        ##        self.pack(fill=BOTH, expand=True)

        ##        frame_cfg = LabelFrame(self._parent, bd=1,  text=u'Конфигурационный файл')
        ##        frame_cfg.pack(fill=BOTH, expand=True, padx=10, pady=10)
        ##        Button(frame_cfg, text='Конфигурация:',justify=RIGHT, command=self.onOpenCfg ).grid(row=0, column=0, sticky=E)
        ##        Label(frame_cfg, textvariable=self._flcfg, justify=LEFT ).grid(row=0, column=1, sticky=W)
        ##        Button(frame_cfg, text=u'Сохранить', command=self.onSave).grid(row=0, column=2, sticky=W+E)

        frame_plc = LabelFrame(self._parent, bd=1, text='Редактирование')
        frame_plc.pack(fill=BOTH, expand=True, padx=10)
        rw = 0
        ##        Button(frame_plc, text=u'Файл со слоями из РЭМПа (*.LTB):', fg='#00F',
        ##            activeforeground='#F00', height=1, justify=RIGHT,
        ##               font=("Times", "14", "bold"),  command=self.onOpenLay).grid(row=rw, column=0, padx=5, pady=5, sticky=W+E)
        ##        Label(frame_plc, textvariable=self._flrmp, justify=LEFT ).grid(row=rw, column=1, sticky=W)
        ##        Button(frame_plc, text=u'Редактировать', command=self.onEditLayRemp).grid(row=rw, column=2, sticky=W)
        rw += 1
        Button(frame_plc, text='Работа с мат-файлами', justify=RIGHT, fg='#11E',
               font=("Times", "14", "bold"), command=self.onEditMat).grid(row=rw, column=0, padx=5, pady=5,
                                                                          sticky=W + E)

        rw += 1
        Button(frame_plc, text='Открыть файл *.PRJ проекта РЭМП', justify=RIGHT, fg='#F22',
               font=("Times", "14", "bold"), command=self.onConfig).grid(row=rw, column=0, padx=5, pady=5, sticky=W + E)

        rw += 1
        self._bfe = Button(frame_plc, text='Редактировать файл оболочек', justify=RIGHT, fg='#11E',
                           font=("Times", "14", "bold"), command=self.onEditLayPech)
        self._bfe['state'] = DISABLED
        self._bfe.grid(row=rw, column=0, padx=5, pady=5, sticky=W + E)
        ##        Label(frame_plc, textvariable=self._fllay, justify=LEFT ).grid(row=rw, column=1, sticky=W)
        ##        Button(frame_plc, text=u'Редактировать', command=self.onEditLayPech).grid(row=rw, column=2, sticky=W)
        ##        rw += 1
        ##        Button(frame_plc, text='Файл с параметрами:', justify=RIGHT, command=self.onOpenPar).grid(row=rw, column=0, sticky=E)
        ##        Label(frame_plc, textvariable=self._flpar, justify=LEFT ).grid(row=rw, column=1, sticky=W)
        ##        Button(frame_plc, text=u'Редактировать', command=self.onEditPar).grid(row=rw, column=2, sticky=W)
        ##        rw += 1
        ##        Button(frame_plc, text='Директория с расчитанными таблицами:',justify=RIGHT,  fg='#22D',
        ##        font=("Times", "14", "bold"),
        ##                command=self.onChoiceTab ).grid(row=rw, column=0, padx=5, pady=5, sticky=W+E)
        ##        Label(frame_plc, textvariable=self._plc_tab, justify=LEFT ).grid(row=rw, column=1, sticky=W)
        rw += 1
        self._btbl = Button(frame_plc, text='Рассчитать распределения', fg='#44B', justify=RIGHT,
                            font=("Times", "14", "bold"), state=self._stbt, command=self.onCalcTbl)
        self._btbl['state'] = DISABLED
        self._btbl.grid(row=rw, column=0, padx=5, pady=5, sticky=W + E)

        rw += 1

        self._btpr = Button(frame_plc, text='Получить распределения для РЭМП', fg='#55A', justify=RIGHT,
                            font=("Times", "14", "bold"),
                            state=self._stbt, command=self.onCalcRmp)
        self._btpr['state'] = DISABLED
        self._btpr.grid(row=rw, column=0, padx=5, pady=5, sticky=W + E)
        rw += 1

        self._btpr1 = Button(frame_plc, text='Распределение для РЭМП в воздухе', fg='#55A', justify=RIGHT,
                             font=("Times", "14", "bold"),
                             state=self._stbt, command=self.onCalcRmp1)
        self._btpr1['state'] = DISABLED
        self._btpr1.grid(row=rw, column=0, padx=5, pady=5, sticky=W + E)
        pass

    ##        Label(frame_plc, textvariable=self._plc_mat, justify=LEFT ).grid(row=rw, column=1, sticky=W)
    ##        Button(frame_plc, text=u'Работа с материалами', command=self.onEditMat).grid(row=rw, column=2, sticky=W)

    ##        frame_p = LabelFrame(self._parent, bd=1, text=u'Вид частицы')
    ##        frame_p.pack(fill=BOTH, expand=True, padx=10, pady=10)
    ##        rbuttonp = Checkbutton(frame_p, text='электроны', variable=self._vapel, state=DISABLED )
    ##        rbuttona = Checkbutton(frame_p, text='фотоны', variable=self._vapph, state=DISABLED )
    ##        rbuttonp.pack(side='left', expand=True)
    ##        rbuttona.pack(side='left', expand=True)

    ##        frame_b = Frame(self._parent, )
    ##        frame_b.pack(fill=X, expand=True, padx=10)
    ##        Button(frame_b, text=u'Сохранить', command=self.onSave).pack(side='right')
    ##        Button(frame_b, text=u'Работать с материалами', command=self.onEditMat).pack(side='left')
    ##        Button(frame_b, text=u'Редактировать слои РЭМПа', command=self.onEditLayRemp).pack(side='left')
    ##        Button(frame_b, text=u'Редактировать оболочки для ПЕЧи', command=self.onEditLayPech).pack(side='left')
    ##        Button(frame_b, text=u'Параметры', command=self.onEditPar).pack(side='left')

    ##        frame_c = LabelFrame(self._parent, bd=1,  text=u'Считаем')
    ##        frame_c.pack(fill=X, expand=True, padx=10,  pady=10)
    ##        Button(frame_c, text=u'Рассчитать Распределения', command=self.onCalcTbl).pack(side='right')
    ##        Button(frame_c, text=u'Рассчитать для РЭМП', command=self.onCalcRmp).pack(side='left')
    ##        Button(frame_c, text=u'Доп. файлы для РЭМП', command=self.onCalcRmp1).pack(side='left')

    ##        Button(frame_c, text=u'Работать с материалами', command=self.onEditMat).pack(side='left')
    ##        Button(frame_c, text=u'Работать со слоями', command=self.onEditLay).pack(side='left')
    ##        Button(frame_c, text=u'Параметры', command=self.onEditPar).pack(side='left')

    def onOpenPath(self):
        self._bd = param.init()
        self._flpar.set(self._bd['par'])
        self._plc_mat.set(self._bd['mat'])
        self._vapel.set(self._bd['electron'])
        self._vapph.set(self._bd['photon'])

    def onOpenProj(self):
        self._bd = param.init()
        self._flpar.set(self._bd['par'])
        self._plc_mat.set(self._bd['mat'])
        self._vapel.set(self._bd['electron'])
        self._vapph.set(self._bd['photon'])

    def modify(self, flnmp):

        nm_lay = read_prj(flnmp)
        nm_ltb = nm_lay.split('.')[0] + '.LTB'
        dr_prj = os.path.dirname(os.path.normpath(flnmp))
        self._bd['proj'] = dr_prj
        self._bd['rmp'] = os.path.normpath(os.path.join(dr_prj, nm_ltb))
        ##            print(ltb)
        dr_tab = os.path.join(dr_prj, 'pechs\\materials')
        xxmkdir(dr_tab)
        self._bd['tab'] = dr_tab
        dr_lay = os.path.join(dr_prj, 'pechs\\initials')
        xxmkdir(dr_lay)

    def onConfig(self):
        """
        """
        self.onOpenProj()  # добавление в ямл новых штук

        try:
            flnmp = projectfilename
        except NameError:
            flnmp = askopenfilename(initialdir=self._bd['home'], title="Выберите файл проекта",
                                    filetypes=[('Файл проекта', '.prj')])

        print(('file {0}'.format(flnmp)))
        if len(flnmp) > 2:
            self._parent.title('Новый проект')
            nm_lay = read_prj(flnmp)
            # print(nm_lay)

            nm_ltb = nm_lay.split('.')[0] + '.LTB'
            print(('Файл с описанием оболочек {}'.format(nm_lay)))
            dr_prj = os.path.dirname(os.path.normpath(flnmp))
            layers, _ = DataParcer(os.path.join(dr_prj, nm_lay)).lay_decoder()

            dr_path = os.path.split(dr_prj)[0]
            # fl_path = os.path.join(dr_path, 'path.config')
            # try:
            #     bd_path = yaml.load(open(fl_path))
            #     print(fl_path)
            # except IOError:
            #     print(('{0} не существует'.format(fl_path)))
            #     print(Exception)
            #     bd_path = {}
            #
            # print(bd_path)
            self._bd['proj'] = dr_prj
            ##            ltb = glob.glob(dr_prj + os.sep +  '*.LTB')
            self._bd['rmp'] = os.path.normpath(os.path.join(dr_prj, nm_ltb))
            # print(self._bd['rmp'])
            ##            dr_tab = os.path.join(dr_prj, 'pechs\\materials')

            pech_path = pech_existance(dr_prj)
            if pech_path == -1:
                return

            if not os.path.exists(os.path.join(pech_path, 'materials')):
                os.mkdir(os.path.join(pech_path, 'materials'))
            if not os.path.exists(os.path.join(pech_path, 'initials')):
                os.mkdir(os.path.join(pech_path, 'initials'))

            dr_tab = os.path.join(pech_path, 'materials')

            # xxmkdir(dr_tab)
            self._bd['tab'] = dr_tab
            self._bd['lay'] = os.path.join(os.path.split(dr_tab)[0], 'initials')
            ##            dr_lay = os.path.join(dr_prj, 'pechs\\initials')
            ##            xxmkdir(dr_lay)
            ft = os.path.join(self._bd['lay'], 'layers')

            # shutil.copyfile(self._bd['rmp'], ft)

            with open(ft, 'w', encoding='utf-8') as file:
                for i in range(len(layers)):
                    file.write(f'{layers[i][0]}\t{layers[i][1]} {layers[i][2]}\n')

            self._bd['lay'] = ft
            # print(self._bd)
            self._bfe['state'] = NORMAL
            self._btbl['state'] = NORMAL

            ##            self._plc_tab.set(self._bd['tab'])
            ##            self._flrmp.set(self._bd['rmp'])
            ##            self._fllay.set(self._bd['lay'])
            ##            self._flcfg.set(self._bd['cfg'])
            self.onEditLayPech()  # запуск окна с выбором мат файлов. до него работа с путями, активация кнопок

    def onElPhoto(self):
        dp = self._bd.copy()
        Process(target=xrun, args=('el_photo_teta', dp)).start()

    def onPhBrems(self):
        dp = self._bd.copy()
        Process(target=xrun, args=('ph_brems_teta', dp)).start()

    def onPhAnig(self):
        dp = self._bd.copy()
        Process(target=xrun, args=('ph_annig_enrg', dp)).start()

    def onCalcTbl(self):  # рассчитать распределения кнопка
        self.onElPhoto()
        self.onPhBrems()
        self.onPhAnig()
        ##        self._bd['electron'] = self._vapel.get()
        ##        self._bd['photon'] =  self._vapph.get()
        ##        self._bd['tab'] = str(self._plc_tab.get())
        ##        self._bd['mat'] = str(self._plc_mat.get())
        ##        self._bd['lay'] = str(self._fllay.get())
        ##        self._bd['cfg'] = str(self._flcfg.get())
        ##        self._bd['par'] = str(self._flpar.get())
        ##        self._bd['rmp'] = str(self._flrmp.get())
        dp = self._bd.copy()
        # Process(target=xrun, args=('calc_tables', dp)).start()
        main_calc_tables(dp)
        messagebox.showinfo('Информация', 'Модуль расчёта распределений закончил свою работу')
        self._btpr['state'] = NORMAL
        self._btpr1['state'] = NORMAL

        materials_path = os.path.join(self._bd['proj'], 'materials')

        try:
            shutil.rmtree(materials_path)
        except:
            pass
        shutil.copytree(self._bd['tab'], os.path.join(self._bd['proj'], 'materials'))

    def onCalcRmp(self):
        """ """
        Process(target=xrun, args=('prtk_table', self._bd)).start()

    def onCalcRmp1(self):
        """ """
        Process(target=xrun, args=('prtk_prtk', self._bd)).start()

    def onExit(self):
        ##        self.onSave()

        self._parent.quit()
        self._parent.destroy()

        if os.path.dirname(__file__) in sys.path:
            sys.path.pop(sys.path.index(os.path.dirname(__file__)))

    def onEditMat(self):
        dp = {'mat': self._plc_mat.get()}
        Process(target=xrun, args=('edit_mat', dp)).start()
        pass

    def onEditLayRemp(self):
        dp = {'lay': self._flrmp.get(), 'mat': self._plc_mat.get()}
        Process(target=xrun, args=('lay_edit', (dp, self._parent))).start()
        pass

    def onEditLayPech(self):
        dp = self._bd.copy()
        Process(target=xrun, args=('lay_edit', (dp, self._parent))).start()
        pass

    def onViewTable(self):
        ftypes = [('Cross-Section', '.23'),
                  ('Elastic', '.526'), ('Brems', '.527'), ('Exit', '.528'),
                  ('Ionization', '.555'),
                  ('Stop Power', '.stp'),
                  ('Average Energy', '.awe'),
                  ('Binding Energy', '.eb'), ('Para Produced', '.516'),
                  ('Stopping Power', '.xer'),
                  ('Compton', '.iv'), ('Coherent', '.cv'), ('All', '.*')]
        ##        dp ={'lay':self._fllay.get(), 'mat':self._plc_mat.get()}
        matFile = askopenfilename(filetypes=ftypes, initialdir=self._bd['tab'])
        if len(matFile) > 5:
            ##        Process(target=xrun, args=('edit_lay', dp)).start()
            fext_ = os.path.splitext(matFile)[1]

            if fext_ in ['.23', '.23p', '.stp']:
                self._ro = askfloat('Плотность материала', 'Можете изменить плотность (г/см^3) ',
                                    initialvalue=self._ro, minvalue=0, maxvalue=10 ** 2)
            if self._ro is None:
                self._ro = 1.0
            ##                print(self._ro)
            dp = {'mtf': matFile, 'ro': self._ro}
            Process(target=xrun, args=('view_table', dp)).start()
        pass

    def onEditPar(self):
        dp = self._bd
        Process(target=xrun, args=('edit_par', dp)).start()
        self._flpar.set(dp['par'])

        pass

    def onSave(self):
        ##        msf = os.path.join(fixWindowsPath(self._msd), name + '.mat')
        # initialfile=self._flcfg.get(),
        flnm = asksaveasfilename(initialdir=self._bd['home'],
                                 title="Сохраняем файл проекта",
                                 filetypes=[('Конфигурационный файл', '.proj')])
        ##        print(flnm)
        if len(flnm) > 1:
            self._parent.title(flnm)
            dz = {}
            ##            self._flcfg.set(os.path.normpath(flnm))
            ##            file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
            for ky in self._kky:
                dz[ky] = str(self._bd[ky])
            ##            sesself._bd['lay'] = str(self._fllay.get())
            ##            self._bd['cfg'] = str(self._flcfg.get())
            ##            self._bd['rmp'] = str(self._flrmp.get())
            with open(flnm, 'w') as ff:
                ff.write(yaml.dump(dz, default_flow_style=False, ))

    def onOpenCfg(self):
        """
        """
        self.onOpenProj()
        ##        print(self._bd)
        flnmp = askopenfilename(initialdir=self._bd['home'], title="Выберите файл",
                                filetypes=[('Конфигурационный файл проекта', '.proj')])
        if len(flnmp) > 2:
            self._parent.title(flnmp)
            ##            self._flcfg.set(os.path.normpath(flnmp) )
            dz = yaml.load(open(flnmp))

            for ky in self._kky:
                self._bd[ky] = dz[ky]
            ##            self._flpar.set(self._bd['par'])
            ##            self._plc_mat.set(self._bd['mat'])
            ##            self._vapel.set(self._bd['electron'])
            ##            self._vapph.set(self._bd['photon'])
            self._bfe['state'] = NORMAL
            self._btbl['state'] = NORMAL
            self._btpr['state'] = NORMAL
            self._btpr1['state'] = NORMAL
        else:
            self.onConfig()

    def onOpenPch(self):
        flnmp = askopenfilename(initialdir=os.path.dirname(self._fllay.get()), title="Выберите файл",
                                filetypes=[('Файл layers', '.*')])
        if len(flnmp) > 2:
            self._fllay.set(os.path.normpath(flnmp))
            self._bd['lay'] = str(self._fllay.get())

    def onOpenLay(self):
        fname = askopenfilename(initialdir=os.path.dirname(self._flrmp.get()), title="Выберите файл со слоями",
                                filetypes=[('Layer  file', '.LTB')])
        if len(fname) > 5:
            self._flrmp.set(os.path.normpath(fname))
            self._bd['rmp'] = str(self._flrmp.get())
            from . import lay_view as em
            ta = Toplevel()
            ##            tm.title(nm + self._mat)
            ta.resizable(False, False)
            ##            tm.geometry("+%d+%d" % (event.x_root, event.y_root))
            dp = self._bd
            ##            dp['lay'] = self._flrmp.get()
            ex = em.Example(ta, dp)
            ta.grab_set()
            ta.focus_set()
            ta.wait_window()
        ##        print(dp['lay'])
        self._fllay.set(dp['lay'])

    def onOpenPar(self):
        fname = askopenfilename(initialdir=os.path.dirname(self._flpar.get()), title="Выберите файл с параметрами",
                                filetypes=[('параметры', '.ini')])
        if len(fname) > 5:
            self._flpar.set(os.path.normpath(fname))
            self._bd['par'] = str(self._flpar.get())

    def onChoiceMat(self):

        msd = askdirectory(initialdir=self._plc_mat.get(), title="Выберите директорию с mat файлами")
        if len(msd) > 5:
            self._plc_mat.set(os.path.normpath(msd))
            self._bd['mat'] = str(self._plc_mat.get())

    def onChoiceTab(self):

        msd = askdirectory(initialdir=self._plc_tab.get(), title="Выберите директорию с распределениями")
        if len(msd) > 5:
            self._plc_tab.set(os.path.normpath(msd))
            self._bd['tab'] = str(self._plc_tab.get())


# def xdialog():
#     er = Tk()
#     ##    er.overrideredirect(True)
#     ex = Example(er)
#     x = (er.winfo_screenwidth() - er.winfo_reqwidth()) / 3
#     y = (er.winfo_screenheight() - er.winfo_reqheight()) / 3
#     er.geometry("+%d+%d" % (x, y))
#     er.mainloop()


if __name__ == '__main__':
    # xdialog()

    try:
        test_file = os.path.join(os.path.dirname(__file__), 'permission_denied_test')

        with open(test_file, 'w') as file:
            file.write('test strig')

    except PermissionError:
        messagebox.showerror('Предупреждение', 'Программа не имеет доступа к файловой системе.\n'
                                               'Запустите программу от имени администратора')

    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

    er = Tk()
    ##    er.overrideredirect(True)
    ex = Example(er)
    x = (er.winfo_screenwidth() - er.winfo_reqwidth()) / 3
    y = (er.winfo_screenheight() - er.winfo_reqheight()) / 3
    er.geometry("+%d+%d" % (x, y))
    er.mainloop()
