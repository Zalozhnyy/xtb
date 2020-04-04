# -*- coding: utf-8 -*-
#!/usr/bin/env python

## @package phisconst
# Данный модуль содержит общие константы и функции.
#
import numpy as np


# Mec^2 in eV
E0 = 0.510998928e+6
Kph=29.1445 # for Iv and Cv photon
Sq2=np.power(2.,0.5)

sl_c = 29979245800.0 # cm/s

alf = 1./137.0360

Re = 0.2817940 #*1.e-14 metr
Re2 = Re**2#*1.e-28 metr or 1.e1 in bar

Avogad = 6.022043446928244e+23
Barns = 1.e-24
AEM = 1.660538921
sig2mu = Avogad*Barns
ms_el_gr = 9.10938356e-4 # 10e-24 gramm
ms_el_aem = 5.48579909070e-4 # a.e.m

ptcl=('ph','el','pz','Pt','Ne') #type of partickle

xW = {}
sig_  ={}
cs_ru = {}
cs_ = {}
sig_[ptcl[0]] = (502,504,516,522)
cs_ru[ptcl[0]] = {sig_[ptcl[0]][0]:'Когерентное рассеяние',
                sig_[ptcl[0]][1]:'Комптоновское рассеяние',
                sig_[ptcl[0]][2]:'Рождение электрон-позитронных пар',
                sig_[ptcl[0]][3]:'Фотоионизация атома'}
cs_[ptcl[0]] = {sig_[ptcl[0]][0]:'Coherent',
                sig_[ptcl[0]][1]:'Compton ',
                sig_[ptcl[0]][2]:'Pair production',
                sig_[ptcl[0]][3]:'Total Photoionization'}
sig_[ptcl[1]] = (526,527,528,522)
cs_[ptcl[1]] = {sig_[ptcl[1]][0]:'Elastic Scattering',
                sig_[ptcl[1]][1]:'Bremsstrahlung ',
                sig_[ptcl[1]][2]:'Excitation',
                sig_[ptcl[1]][3]:'Total Electroionization'}
cs_ru[ptcl[1]] = {sig_[ptcl[1]][0]:'Упругое рассеяние',
                sig_[ptcl[1]][1]:'Тормозное излучение ',
                sig_[ptcl[1]][2]:'Возбуждение',
                sig_[ptcl[1]][3]:'Полная электроионизация'}

sig_[ptcl[2]] = (526,527,528,522)
cs_ru[ptcl[2]] = {sig_[ptcl[1]][0]:'Упругое рассеяние',
                sig_[ptcl[1]][1]:'Тормозное излучение ',
                sig_[ptcl[1]][2]:'Возбуждение атома',
                sig_[ptcl[1]][3]:'Электроионизация атома'}
cs_[ptcl[2]] = {sig_[ptcl[1]][0]:'Elastic Scattering',
                sig_[ptcl[1]][1]:'Bremsstrahlung ',
                sig_[ptcl[1]][2]:'Excitation',
                sig_[ptcl[1]][3]:'Total Electroionization'}


epic = '''2014 ИПМ РАН'''

def create_parser(name, desc):
    try:
        import argparse
        import textwrap

        parser = argparse.ArgumentParser(
         prog = name,
         formatter_class = argparse.RawDescriptionHelpFormatter,
         fromfile_prefix_chars = '@',
         description=textwrap.dedent(desc),
          epilog=epic,
          add_help = False)
        parent_group = parser.add_argument_group (title='Параметры')
        parent_group.add_argument ('--help', '-h', action='help', help='Справка')
        parent_group.add_argument("-g", "--grafic", action = 'store_true', help="выводит таблицы в графическом представлении")
        parent_group.add_argument('-f', '--file', action = 'store_false', help = 'не сохранять таблицы в файле')
        return parser
    except ImportError:
        print("версия python < 2.7")
        return None



def qar(ee_,nn_):

    Qmax=Kph/E0*ee_Sq2
    qq_=np.linspace(0.0,Qmax,nn_)
    xx_=1-(E0*qq_/Kph/ee_)**2
    xx_=xx_[::-1]
    xx_[0]=-1.
    xx_[-1]=1.
    return qq_,xx_



def xxFactor(En_, cost_,Kv_ = -1):
    """
       Kv in (0,1) r-Kline-Nishina(Kv=1), Kv=2 - Tomson(Kv=2)
       cost_ - cos(tet)
    """
    if Kv_ == 1 or Kv_ == 0:
        Et_ = En_/E0
        ee_ = np.tile(Et_,(len(cost_), 1))
        ct_ = np.tile(cost_,(len(En_), 1));ct_ =np.transpose(ct_)
        Fm_ = (1+ct_**2+(ee_*(1-ct_))**2/(1.0+ee_*(1.0-ct_)))/(1.0+ee_*(1.0-ct_))**2
    elif Kv_ == 2:
        F_ = 1 + cost_**2
        Fm_ = np.tile(F_,(len(En_),1))
        Fm_ = np.transpose(Fm_)
    else:
        exit(-1)
    return Fm_

def xxInitElement(name):
    """
    Initialize the initial data for elements
    """
    with open(name,'rt') as xFl:
        bE={}
        sN={}
        d={}
        for line in xFl:
            t=line.split()
            bE[int(t[0])]=[(chr(int(t[1]))+chr(int(t[2]))).strip(),float(t[3]),float(t[4])]
    for k in list(bE.keys()):
        sN[bE[k][0]]=int(k)
    return  (bE,sN)


if __name__ == '__main__':
    Ee_ = np.logspace(2, 7, 51)
    Xx_ = np.linspace(-1,1,101)

    t2_ = xxFactor(Ee_, Xx_, Kv_ = 2)
    t1_ = xxFactor(Ee_, Xx_, Kv_ = 1)

    pass
    #plt.plot(Xx_,t1_)
