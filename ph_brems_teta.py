#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package ph_brems_teta
# Модуль для построения распределения косинуса угла тормозного фотона
# при взаимодействии электрона с веществом
#-------------------------------------------------------------------------------

import os
##import  time

import numpy as np
import xxfun as xox
import interface as xItf
import xxplot as xxp


import phisconst as phis

bFile_ = True
bGraf_ = False

xgsave= False
xgrafic = False
xfile = True


class Bremteta():
    """
    """
    _a0 = 0.625
    _d0 = 27.0
    _c0 = 9 * _a0 ** 2 / (9.0 + _d0)


    def cumanglbrem (self,xi0_, k) :
        """
        calc fun
        """
        p0_ = self._a0*k*xi0_
        e1_ = np.exp(-p0_)
        e3_ = np.power(e1_, 3)
        rr_ = 9. + self._d0 - 9. * (1+p0_)*e1_ - self._d0*(3*p0_+1)*e3_
        return rr_

    def anglbrem (self,xi0_, k) :
        """
        calc fun
        """
        p0_ = k*xi0_
        e1_ = np.exp(-p0_)
        e3_ = np.power(e1_, 3)
        rr_ = p0_*e1_ + self._d0*p0_*e3_
        return rr_
    def calc_table(self, ee_, gm_, nt_, kLog, db):
        """
        """
        kk_=ee_/phis.E0
        if kLog:
            tet_ = np.linspace(-18,-1, nt_)

            tet_=np.power(10.,tet_)
            tet_=np.insert(tet_,0,0.0)
            tet_=np.append(tet_,np.linspace(0.1, np.pi, nt_))
        else:
            tet_ = np.linspace(0, np.pi, nt_)
        tetg_ = np.cos(tet_)
        rr_ = []
        av=[]
        mpdf_ = []
        kFr=True


        for i,k in enumerate(kk_):
            if kLog or kFr:
                dd_ = self.cumanglbrem(tet_, k)


                dd_ /= dd_[-1] # normirovka
                tt_=np.cos(tet_)
                dd_=1.-dd_


                rc=xox.xxInterp1(dd_[::-1],tt_[::-1],gm_)
                vt_ = xox.xxTrapz(gm_, rc)
                if vt_ > 0.95:
                    kFr=False
                # print('for E=%e cos average - %f' %(ee_[i], vt_))
                xt_=self.anglbrem(tet_, k)
                xt_/=np.max(xt_)
            else:
                rc=np.ones(len(gm_),)
                xt_ = np.zeros((len(tet_),))
                xt_[-1] = 1.
                vt_=1.
            av.append(vt_)
            rr_.append(rc)
            mpdf_.append(xt_)

        dm_ = np.array(rr_)
        if xfile:
            ss='# Output: distribution  cos(tet) of photon'
            if kLog:
                xox.xWrite3_log(os.path.join(db['tab'], 'brem_ph_log'), ee_,gm_,dm_,ss)
            else:

                xox.xWrite3_lin(os.path.join(db['tab'], 'brem_ph_lin'), ee_,gm_,dm_,ss)
        self.vv_=dm_
        print(ss)
        return dm_, np.array(mpdf_), tetg_, av


def main(db):

##    dir_ = os.getcwd()
    xI=xItf.Init(nFile=db['par'])
    Emin=xI.xin['Emin']
    Emax=xI.xin['Emax']
    nE=xI.xin['nE']
    ee_=np.logspace(Emin,Emax,nE)
##    ee_=np.array([50e3, 100e3, 500e3])

    kLog_ = 1
    if kLog_:
        gg_ = np.array([0.0,])
        tem_ = np.logspace(-12, 0, 2**10 - 1)
        gg_ = np.append(gg_, tem_)
    else:
        gg_ = np.linspace(0., 1., 2**10)
    nt = 2**10
    lbrem_ = True
    fig_ =0;
    A = Bremteta()
    yy_, pdf_, xt_, ave_ = A.calc_table(ee_, gg_, nt, kLog_, db)
    if xgrafic:

        fig_ += 1
        xxp.xtable_plot(ee_, gg_, yy_, fig_, bxlog = False, bylog = False,
                        ylabel = r'$cos(\theta_{\gamma})$', xlabel = r'$\xi$' )
        if xgsave:xxp.xsave_fig('brem_table')
        fig_ +=1
        xxp.xtable_polar(ee_, xt_, pdf_, fig_)
        if xgsave:xxp.xsave_fig('brem_directrissa')
        fig_ +=1
        opis_ = {'legenda':('Средний косинус',),
         'ylabel':r'$\widehat{cos(\theta_{\gamma})}$', 'bxlog': True,
         'bylog':False, 'xlabel':r'$\varepsilon_{e^-}, eV$', 'place':'upper left'}

        xxp.xgraf_plot(ee_, ave_, fig_, opis_,)
        if xgsave:xxp.xsave_fig('brem_average')
        xxp.xshw()


def create_parser():
    parser = argparse.ArgumentParser(
     prog='ph_brems_teta.py',
     formatter_class=argparse.RawDescriptionHelpFormatter,
     fromfile_prefix_chars='@',
     description=textwrap.dedent('''\
     Расчет таблиц для розыгрыша косинуса угла фотона рождённого
     при тормозном излучении электрона
     -----------------------------------------
         '''),
         epilog=phis.epic,
         add_help = False
         )
    parent_group = parser.add_argument_group (title = 'Параметры')
    parent_group.add_argument ('--help', '-h', action=  'help', help='Справка')

    parent_group.add_argument("-g", "--grafic", action = 'store_true', help = "выводит таблицы в графическом представлении")
    parent_group.add_argument('-f', '--nofile', action = 'store_false', help = 'не сохранять таблицы в файле')

    return parser

if __name__ == '__main__':
    try:
        import argparse
        import textwrap

        parser = create_parser()
        #namespace = parser.parse_args(sys.argv[1:])

        args_= vars( parser.parse_args())
        xgrafic = args_['grafic']
        xfile = args_['nofile']

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
