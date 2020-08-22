#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package Program
# Модуль для построения энергетических и угловых распределений
# фотонов и электронов при их взаимодействии с веществом
#-------------------------------------------------------------------------------

import os
import  time
import numpy as np

import xtb_electron as xEl
import interface as xItf
import xtb_photon as xPh
import phisconst as phis

bPhoton = True
bElectron = True
iMat = True

setk_ = 'parameter.ini'
compz_ = 'compozits'
lay_ = 'layers'

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
        print(("такого файла наверное нет.\n%s" % nmfl))
        exit(-1)
    nv = []
    for lr in lfn:
        lr = lr.split()
        nv.append(lr[1])
    nnv = np.union1d([], nv)
    return nnv


def proga(setk_, matfile):
    """
    """
    idir = os.getcwd()
    print(("Файл с параметрами выходных сеток - {0}".format(setk_)))
    ##    Считываем информацию о параметрах выходных сеток
    xI = xItf.xxInit(nExePath = idir, nFile = os.path.join(idir, setk_))
    matfile = read_layer(os.path.join(idir, lay_), nmfl='')
    for matFie_ in matfile:
        matFie_ = matFie_.lower()
        print(("Обрабатывается файл - {0}".format(matFie_)))
        idmat = os.path.join(idir, 'mat-files' )
        matFile=os.path.join(idmat, matFie_ + '.mat')
        ##    Считываем информацию о заданных композитах
        Obt = xItf.xObject(matFile, xI.sN)
        ##    Сохраняем информацию о композитах и и оболочках
##        Obt.Ro2file(os.path.join(idir, 'ro.txt'))
##        Obt.Sh2file(os.path.join(idir, 'surfaces'))
##        Obt.Mt2file(os.path.join(idir, 'materials'))

        path, nmFile = os.path.split(matFile)
        NmFile, ExtFile = os.path.splitext(nmFile)

        tBegin = time.clock()
        ##    Цикл по заданным композита
        for k, mt in enumerate(Obt.vv):
            Mt = xItf.Material(mt[k])
            if bPhoton:
                print('Вычисляем таблицы распределений для фотонов')
                if iMat:
                    ## Строим энергетические и угловые распределения для фотонов для текущего композита
                    xPh.ph_mat(xI, Mt, matFile)
                    print((time.clock() - tBegin))

                else:
                    pass

            if bElectron:
                print('Вычисляем таблицы распределений для электронов')
                if iMat:
                    ## Строим энергетические и угловые распределения для электронов для текущего композита
                    xEl.el_mat(xI, Mt, matFile)
            else:
                    pass
            tEnd = time.clock()
            print(('time = {0}'.format(tEnd - tBegin)))

def create_parser():
    parser = argparse.ArgumentParser(
     prog='PROG',
     formatter_class=argparse.RawDescriptionHelpFormatter,
     fromfile_prefix_chars='@',
     description=textwrap.dedent('''\
Модуль для построения энергетических и угловых распределений фотонов и
электронов при их взаимодействии с веществом
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Пример 1:
    Program.py
    Строятся энергетические и угловые распределения фотонов и электронов.
    Используется файл композитов compozits и файл выходных сеток parameter.ini
Пример 2:
    Program.py -e
    Строятся энергетические и угловые распределения только для фотонов.
    Используется файл композитов compozits и файл выходных сеток parameter.ini
Пример 3:
    Program.py -с matal -s parm
    Строятся энергетические и угловые распределения только для фотонов.
    Используется файл композитов matal и файл выходных сеток parm
          '''),
         epilog=phis.epic,
         add_help = False
         )
    parent_group = parser.add_argument_group (title='Параметры')
    parent_group.add_argument ('--help', '-h', action='help', help='Справка')
##    parent_group.add_argument ('-c', '--composite', nargs = '+',  action = 'store', type=str,
##            help = u'Файл формата compozits' , default = [compz_])

    parent_group.add_argument ('-l', '--layers',   action = 'store', type=str,
            help = 'Файл формата layers' , default = lay_)

    parent_group.add_argument ('-s', '--setka', action = 'store', type=str,
            help = 'Файл формата parameter.ini' ,default = setk_)

    parent_group.add_argument("-p", "--photon", action = 'store_false',
                            help = "не будут вычисляться распределения для фотонов")
    parent_group.add_argument('-e', '--electron', action = 'store_false',
                            help = 'не будут вычисляться распределения для электронов')

    return parser


if __name__ == '__main__':
    """
    """
    try:
        import argparse
        import textwrap

        parser = create_parser()
        #namespace = parser.parse_args(sys.argv[1:])

        args_= vars( parser.parse_args())
        bPhoton = args_['photon']
        bElectron = args_['electron']
        setk_ = args_['setka']
##        compz_ = args_['composite']
        lay_ = args_['layers']
        idir = os.getcwd()
        proga(setk_, lay_)
    except ImportError:
        print("версия python < 2.7")
        proga(setk_, lay_)
        pass
    ##    exit(0)
    finally:
            pass

