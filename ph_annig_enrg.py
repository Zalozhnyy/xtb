#!/usr/bin/env python
# -*- coding: utf-8 -*-
## @package ph_annig_enrg
# Модуль для получения распределения энергии позитрона при рождении пар
#
#-------------------------------------------------------------------------------

import os
import sys
import numpy as np

import kiadf.xxfun as xox
import kiadf.phisconst as phis
import kiadf.interface as xItf
import kiadf.xxplot as xxp


xloc_ = {}
xloc_['bgraf_save'] = False
xloc_['bgraf_display'] = False
xloc_['bgm_log'] = False
xloc_['bfile'] = True
xloc_['slin_file'] = 'annig_lin'

xgsave= False
xgrafic = False
xfile = True
def sigma_annig(T):
    """
    k=T/E0 + 1
    """
    ZZ_  =1
    T = np.array(T)
    k = T/phis.E0 + 1
    cg_ = ZZ_ * np.pi * phis.Re2 / (k + 1) * ((k ** 2 + 4 * k + 1) / (k ** 2 - 1) * np.log(k + np.sqrt((k ** 2 - 1)))
     - ((k + 3) / np.sqrt(k ** 2 - 1)))
    return cg_


class AnnigPozitron():
    """
    T -Kinetic energy of pozitron
    """
    sig_=[]

    def intpdf(self, y_, x):
        """
        """
    ##    rr_ = (x * (yk ** 2 + 4 * yk + 1) * np.log(x) + 1 - ((yk + 1) ** 2) * x ** 2) / ((yk + 1) ** 2) / x/(yk-1)
        rr_ = (-x + 1/x+np.log(x)*(2*y_**3 + 5*y_**2 + 4*y_ + 1))/(y_-1)

        return rr_


    def calc_table(self, lT_, gm_,  db, kLog = 0,):
        """
        """
        k=lT_/phis.E0+1
        # vv_=sigma_annig(k)
        self.tbl_=[]
        self.pdf_ = []
        self.E_ = []
        av_ =[]
        for i,T in enumerate(lT_):
            Et_=T+2*phis.E0
            yk=k[i]
            tt_=0.5*np.sqrt(T / (T + 2.0*phis.E0))
            Emin = 0.5 - tt_
            Emax = 0.5 + tt_
            x_=np.linspace(Emin,Emax,16*len(gm_))
            cg_ =  (1 + 2 * yk / (yk + 1) ** 2 - x_ - 1. / (yk + 1) ** 2 / x_)
            cg_ /=x_*(yk - 1)
            xx_ =x_*Et_
            iS_ = self.intpdf(yk, x_[-1]) - self.intpdf(yk, x_[0])
            cg_/=iS_
            IpDf_ = self.intpdf(yk, x_[:]) - self.intpdf(yk, x_[0])
            IpDf_/=IpDf_[-1]
            self.pdf_.append(IpDf_)
            self.E_.append(x_)
            t_=np.interp(gm_,IpDf_,x_)
            tt_=t_*Et_

            self.tbl_.append(tt_)
            tt_ = np.trapz(tt_, gm_)
            av_.append(tt_)
        if xfile:
            dm_=np.log10(self.tbl_)
            ss='# Output: distribution logarithm energy of photon'
            if kLog:
                xox.xWrite3_log(os.path.join(db['tab'], 'annig_log'), lT_,gm_,dm_,ss)
            else:
                xox.xWrite3_lin(os.path.join(db['tab'], 'annig_lin'), lT_,gm_,dm_,ss)
            print(ss)
        return np.array(self.tbl_), av_


def main(db):
    """
    """
    #print(u'Вычисление распределения энергии одного из фотонов при аннигиляции позитрона')

    ee_ = np.logspace(2, 7, 6)
    dir_ = os.getcwd()
    xI=xItf.Init(nFile= db['par'])
    Emin=xI.xin['Emin']
    Emax=xI.xin['Emax']
    nE=xI.xin['nE']
    nG = xI.xin['nG_annig']
##    self.nE=xin['En']
    ee_=np.logspace(Emin,Emax,nE)

    kLog_ = False
    if kLog_:
        gg_=np.logspace(-12, 0, nG-1)
        gg_=np.insert(gg_, 0, 0.0)
    else:
        gg_ = np.linspace(0., 1., nG)

##    sig_ = sigma_annig(ee_)
    pass
    tt_ = AnnigPozitron()
    dm_, ave_ = tt_.calc_table(ee_, gg_, db, kLog = kLog_)

    if xgrafic:
        fig_ = 1
        xxp.xtable_plot(ee_, gg_, dm_, fig_, bxlog = False, bylog = True,
                        ylabel = r'$\varepsilon_{\gamma}, эВ$', xlabel = r'$\xi$' )
        if xgsave:xxp.xsave_fig('annihilation')
        fig_ +=1
        opis_ = {'legenda':('Средняя энергии фотона при аннигиляции',),
         'ylabel':r'$\widehat{\varepsilon_{\gamma}} эВ$', 'bxlog': True,
         'bylog':True, 'xlabel':r'$\varepsilon_{e^+}, eV$', 'place':'upper left'}

        xxp.xgraf_plot(ee_, ave_, fig_, opis_,)
        if xgsave:xxp.xsave_fig('annihilation_brem_average')
        xxp.xshw()

def create_parser():

    parser = argparse.ArgumentParser(
     prog='ph_annig_enrg.py',
     formatter_class=argparse.RawDescriptionHelpFormatter,
     fromfile_prefix_chars='@',
     description=textwrap.dedent('''\
 Расчет таблиц для розыгрыша энергии одного из фотона
 при аннигиляции позитрона
 -------------------------------------------------------------
   Пример 1:
        ph_annig_teta.py
        Вычисляется распределение и результаты записываются в файл
   Пример 2:
        ph_annig_teta.py -f -g
        Вычисляется распределение и результаты выодятся на экран
        Запись в файл не производится
         '''),
      epilog=phis.epic,
      add_help = False)
    parent_group = parser.add_argument_group (title='Параметры')
    parent_group.add_argument ('--help', '-h', action='help', help='Справка')
    parent_group.add_argument("-g", "--grafic", action = 'store_true', help="выводит таблицы в графическом представлении")
    parent_group.add_argument('-f', '--file', action = 'store_false', help = 'не сохранять таблицы в файле')
    return parser

if __name__ == '__main__':

    try:
        import argparse
        import textwrap
        parser = create_parser()
        args_= vars( parser.parse_args())
        xgrafic = args_['grafic']
        xfile = args_['file']
        file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
        ff = open(file_name, 'r')
        bd =  yaml.load(ff)
        main(bd)
    except ImportError:
        print("версия python < 2.7")
        main(bd)
    else:
        pass
    finally:
        pass