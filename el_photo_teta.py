#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package el_photo_teta
# Модуль для получения распределения косинуса угла электрона
# при фотопоглощении фотона
#-------------------------------------------------------------------------------

import os
##import  time
import yaml
import numpy as np


import xxfun as xox
import interface as xItf
import xxplot as xxp


import phisconst as phis

bFile_ = True
bGraf_ = True

xgsave= False
xgrafic = False
xfile = True


class Photo():
    """
    """
    def calc_table(self, ee_, gm_, nt_,kLog):
        """
        """
        kk_=ee_/phis.E0
        bet_=np.sqrt(kk_*(kk_+2))/(kk_+1)
        gg_=1+kk_

        xx_ = np.linspace(-1, 1, nt_)
        tet_ = xx_
        rr_ = []
        av = []
        mpdf_ = []
        kFr=True

        for i,k in enumerate(kk_):
            if kLog or kFr:
                lr_ = (1. - np.power(xx_, 2))/np.power(1. - bet_[i]*xx_, 4)
                ff_ = 1. + 0.5*(gg_[i] - 1.)*(gg_[i] - 2.)*(1. - bet_[i]*xx_)
                pDf_ = lr_ * ff_
                CpDf_ = xox.xxCumTrapz(xx_, pDf_)
                IpDf_ = CpDf_/CpDf_[-1] # normirovka
                tbl_ = np.interp(gm_,IpDf_, xx_)
                vt_=xox.xxTrapz(gm_,tbl_)
                if vt_>0.99:
                    kFr=False
                    # print('for E=%e cos average - %f' %(ee_[i],vt_))
                xt_ = pDf_ /np.max(pDf_)
            else:
                rc=np.ones(len(gm_),)
                xt_ = np.zeros((len(tet_),))
                xt_[-1] = 1.
                vt_=1.
            av.append(vt_)
            rr_.append(tbl_)
            mpdf_.append(xt_)

        dm_ = np.array(rr_)
        self.vv_=dm_

        return dm_, np.array(mpdf_), tet_, av

def main(db):
    print('El-photo_teta start')
##    dir_ = os.getcwd()
    xI=xItf.Init(nFile= db['par'])
    Emin=xI.xin['Emin']
    Emax=xI.xin['Emax']
    nE=xI.xin['nE']
    # self.nE=xin['En']
    ee_=np.logspace(Emin,Emax,nE)

    kLog_ = 1
    if kLog_:
        gg_ = np.array([0.0,])
        tem_ = np.logspace(-12, 0, 2**10 - 1)
        gm_ = np.append(gg_, tem_)
    else:
        gm_ = np.linspace(0., 1., 2**10)
        # tet = np.linspace(0, np.pi, 501)
    nt = 2**10
    fig_ =0;
    A = Photo()
    yy_, pdf_, xt_, ave_ = A.calc_table(ee_, gm_, nt, kLog_)
    if xfile:
        ss='# Output: distribution  cos(tet) of electron'
        if kLog_:
            xox.xWrite3_log(os.path.join(db['tab'], 'photo_log'), ee_,gm_,yy_,ss)
        else:

            xox.xWrite3_lin(os.path.join(db['tab'], 'photo_lin'), ee_,gm_,yy_,ss)
    print(ss)
    if xgrafic:

        fig_ += 1
        xxp.xtable_plot(ee_, gm_, yy_, 'F_photo', bxlog = False, bylog = False,
                        ylabel = r'$cos(\theta_{e^-})$', xlabel = r'$\xi$' )
        xxp.xsave_fig('para_table')
        fig_ +=1
        xxp.xtable_polar(ee_, xt_, pdf_, 'IND_photo')
        fig_ +=1
        opis_ = {'legenda':('Средний косинус',),
         'ylabel':r'$\widehat{cos(\theta_{e^-})}$', 'bxlog': True,
         'bylog':False, 'xlabel':r'$E_{e^-}, eV$', 'place':'upper left'}
        xxp.xsave_fig('para_directrissa')

        xxp.xgraf_plot(ee_, ave_, 'mE_pozitron', opis_,)
        if xgsave: xxp.xsave_fig('para_average')
        xxp.xshw()

def create_parser():

    parser = argparse.ArgumentParser(
     prog='el_photo_teta.py',
     formatter_class=argparse.RawDescriptionHelpFormatter,
     fromfile_prefix_chars='@',
     description=textwrap.dedent('''\
 Расчет таблиц для розыгрыша косинуса угла
 электрона рождённого при фотопоглощении
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
        # print(args_)
        file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
        ff = open(file_name, 'r')
        bd =  yaml.load(ff)
        main(bd)
    except ImportError:
        print("версия python < 2.7")
        main(bd)
        pass
    ##    exit(0)
    finally:
            pass
