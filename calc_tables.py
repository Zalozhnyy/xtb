#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package Program
# Модуль для построения энергетических и угловых распределений
# фотонов и электронов при их взаимодействии с веществом
# -------------------------------------------------------------------------------

import os, sys
import time
import math
import numpy as np
import yaml

from multiprocessing.dummy import Process

import kiadf.phisconst as phis
import kiadf.interface as xItf
import kiadf.electron as xel
import kiadf.photon as xph

from tkinter import messagebox as mb

import cfg

bPhoton = True
bElectron = True
iMat = True

setk_ = 'parameter.ini'
compz_ = 'compozits'


def write_file_mat(nfl, mt):
##    comp = self.conver()
    with open(nfl,'w') as ff:
        ff.write('[Composite]\t%s\n' % mt['Composite'])
        for el in mt['Element']:
            ss ='[Element]\t%s\t%f' % (el[0], el[1])
            if len(el) == 3 and el[2] > 0:
                ss += '\t%d\n' % (el[2])
            else:
                ss +='\n'
            ff.write(ss)
        ff.write('[Density]\t%f\n' % mt['Density'])


def xrun(modname, args):
    print(modname)
    module = __import__(modname)
    module.main(args)


def read_layer(ss, nmfl='layers'):
    """
    """
    nf = os.path.join(ss, nmfl)
    if len(nmfl) == 0:
        nf = ss
    try:
        with open(nf, 'r') as ff:
            lfn = ff.readlines()
    except IOError:
        print("такого файла наверное нет.\n%s" % nmfl)
        return []
    nv = []
    for lr in lfn:
        lr = lr.split()
        nv.append(lr[1].lower() + '.' + cfg.val.extmat)
    nnv = np.union1d([], nv)
    return nnv


def main(db):  # setk_, matfile):
    """
    """
    idir = os.getcwd()
    print(("Файл с параметрами выходных сеток - {0}".format(db['par'])))
    ##    Считываем информацию о параметрах выходных сеток
    xI = xItf.Init(nExePath=db['tab'], nFile=db['par'])
    print(("Файл с описанием оболочек - {0}".format(db['lay'])))
    matfile = read_layer(db['lay'], nmfl='')
    ##    print(matfile)

    with open((os.path.join(db['tab'], 'materials')), 'wt') as ff:
        for mm in matfile:
            ##            print(mm)
            ff.write('{0:s}\n'.format(os.path.splitext(mm)[0]))

    for matFie_ in matfile:
        print(("Обрабатывается файл - {0}".format(matFie_)))
        matFile = os.path.join(db['mat'], matFie_)
        layers = os.path.abspath(db['lay'])
        ##    Считываем информацию о заданных композитах
        Obt = xItf.Object(matFile, xI.sN, matFie_, layers)
        ##    Сохраняем информацию о композитах и и оболочках
        ##        Obt.Ro2file(os.path.join(idir, 'ro.txt'))
        ##        Obt.Sh2file(os.path.join(idir, 'surfaces'))
        ##        Obt.Mt2file(os.path.join(db['tab'], 'materials'))

        path, nmFile = os.path.split(matFile)
        NmFile, ExtFile = os.path.splitext(nmFile)

        # tBegin = time.clock()
        ##    Цикл по заданным композита
        for k, mt in enumerate(Obt.vv):
            Mt = xItf.Material(mt[k])
            if bPhoton:
                print('Вычисляем таблицы распределений для фотонов')
                if db['photon']:
                    ## Строим энергетические и угловые распределения для фотонов для текущего композита
                    xph.main(xI, Mt, matFile, db['tab'])
                ##                    module = __import__('kiadf.photon')
                ##                    dp = {'xI': xI,'Mt':  Mt, 'mf': matFile, 'path': db['tab']}
                ##                    print(dp['xI'].xin)
                ##                    print(dp['Mt'])
                ##                    Process(target=xrun, args=('photon', dp)).start()

                # print((time.clock() - tBegin))

                else:
                    pass

            if db['electron']:
                print('Вычисляем таблицы распределений для электронов')
                if iMat:
                    ## Строим энергетические и угловые распределения для электронов для текущего композита
                    xel.main(xI, Mt, matFile, db['tab'])
            ##                    Process(target=xrun, args=('kiadf.electron', xI, Mt, matFile, db['tab'])).start()
            else:
                pass
            mt[k]['Composite'] = mt[k]['Composite'].upper()
            mt_ = 'mat-' + mt[k]['Composite']
            fl_mat_ = os.path.join(db.get('tab', ''), mt_,
                                   mt[k]['Composite'].lower() + '.' + cfg.val.extmat)
            write_file_mat(fl_mat_, mt[k])

        # tEnd = time.clock()
        # print(('time = {0}'.format(tEnd - tBegin)))
        # mb.showinfo('Информация', 'Модуль расчёта распределений закончил свою работу')
        print('Модуль расчёта распределений закончил свою работу')


if __name__ == '__main__':
    """
    """
    file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
    ff = open(file_name, 'r')
    bd = yaml.load(ff)

    main(bd)
    exit(0)
    try:
        file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
        ff = open(file_name, 'r')
        bd = yaml.load(ff)

        main(bd)
    except:
        print("Что-то пошло не так")
        pass
    ##    exit(0)
    finally:
        pass
