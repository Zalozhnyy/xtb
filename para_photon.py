# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name: calculate energetic distribution for electron-pozitron
# Purpose:
#
# Author: Podolyko
#
# Created:     03.12.2012
# Copyright:   (c) december 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os, sys

import numpy as np
import xxplot as xxp

##try:
##    import matplotlib.pyplot as plt
##except:
##    xGraff=False
##else:
##    xGraff=True
##    from matplotlib import rc
##    font = {'family': 'Verdana',
##            'weight': 'normal'}
##    rc('font', **font)


import xxfun as xox

import phisconst as phis


def module_path():
    """ """
    if hasattr(sys, "frozen"):
        return os.path.dirname(
            str(sys.executable, sys.getfilesystemencoding( ))
        )
    return os.path.dirname(os.path.abspath
        (str(__file__, sys.getfilesystemencoding( ))))


def v(a,k):
    """
    """
    cl = np.log((4. / k))
    cg = ((0.2840e0 - 0.1909e0 * a) * cl +
    (0.1095e0 + 0.2206e0 * a) * np.power(cl, 2)
    + (0.2888e-1 - 0.4269e-1 * a) * np.power(cl, 3) +
    (0.2527e-2 + 0.2623e-2 * a) * np.power(cl, 4))
    ce = 1-np.exp(-cg)
    return ce

def ffC(a):
    """
    """
    cg_ = ((a ** 2) * (1.0 / (1 + a ** 2) + 0.202059e0 - 0.3693e-1 * (a ** 2) +
    0.835e-2 * (a ** 4) - 0.201e-2 * (a ** 6) + 0.49e-3 * (a ** 8) -
    0.12e-3 * (a ** 10) + 0.3e-4 * (a ** 12)))
    return cg_

def FF(a):
    ff_ = np.zeros((4,1))
    ff_[0] = (-0.1774e0 - 0.121e2 * a + 0.1118e2 * a**2)
    ff_[1] = (0.8523e1 + 0.7326e2 * a - 0.4441e2 * a**2)
    ff_[2] = -(0.1352e2 + 0.1211e3 * a - 0.9641e2 * a**2)
    ff_[3] = (0.8496e1 + 0.6205e2 * a - 0.6341e2 * a**2)
    return ff_


def xxInitPara(name):
    """
    Initialize the initial data for elements
    """
    with open(name,'rt') as xFl:
        bP = {}
        for line in xFl:
            t = line.split()
            bP[int(t[0])] = [float(t[1]), float(t[2])]
    return bP

class Paraep():
##    Re = 0.2817940
##    Re2 = Re**2#*1.e-4


    def calc_table(self, Z, Eph, gm_, kLog=1):
        """
        """
        Eph=np.array(Eph)
##        sDir=module_path()
        sDir = os.path.dirname(__file__)
        pP=xxInitPara(os.path.join(sDir,'para.txt'))
        # all parametrs
        #E0=0.511E+6
        Cr = 1.0093
        #alf = 1./137.
        # parameters from Z
        self.a = phis.alf*Z
        Rm = pP[Z][0]
        eta = pP[Z][1]
        lRm = 4.0*np.log(Rm)
        self.fC = ffC(self.a)
        ff = FF(self.a)

##        Eph=np.logspace(6+np.log10(1.5),6+np.log10(200),21)
##        Eph = [1.5, 2.5,5,10,20,50,200]
##        Eph = np.array(Eph)*1.e6
    ##    Eph=np.array([1.5e+6, 2.e6]);
    ##    EphK=np.power(10,Es)
        EphK = Eph/phis.E0
        kE = 2./EphK
        Eta = v(self.a,kE)*eta
        fC = 2*phis.Re2*Z*(Z+Eta)*phis.alf/3.
        F = ff[0]*np.power(kE,1./2.)
        for j in range(1,4):
            F += ff[j]*np.power(kE, (j+1)/2.)
        Eave=[]
        pdf_ = []
        vv_ = []
        Eem_ = []
        for i,k in enumerate(EphK):
            if k > 2.: #Eph>2*mc**2
                Eel = np.linspace(0.e-3, k-2.,len(gm_))
                cs1=np.logspace(-12,np.log10(k-2.),len(gm_)-1)
                cs1=np.insert(cs1,0,0.0)
        ##        cs1=np.logspace(-12,math.log10(2),100)
                cs2=k-2.-cs1
                cs=np.union1d(cs1,cs2)
                ics=(cs==0.)
    ##            cs[ics]=10**(-16)

                Eel=cs1

##                Eel = np.logspace(-16, np.log10(k-2), len(gm_))
                Ee = Eel*phis.E0
                eps = (Eel+1.)/k
                b = (Rm / k / eps / (1 - eps)) / 2.0
                b2 = np.power(b, 2)
                F1_ = 2.0 - 2.0 * np.log((1 + b2)) - 4.0 * b * np.arctan(1.0/b)+ lRm
                F2_ = 4.0/3.0 - 2.0 * np.log((1 + b2)) + 2.0*(b2)*(4.-4.*b*np.arctan(1./b)-3.*np.log((1.+1./b2)))+ lRm
                g1_ = (3*F1_ - F2_)/2. - lRm
                g2_ = (3*F1_ + F2_)/4.-lRm
                g0_ = lRm - 4.0 * self.fC + F[i]
                fF1_ = g1_ + g0_
                fF2_ = g2_ + g0_
                dSig = (2  *np.power(0.5 - eps, 2)*fF1_ + fF2_)
                dSig *= fC[i]
                Smin_=np.min(dSig)
##                print (Smin_)
##                dSig-=Smin_
    ##            plt.plot((Ee+phis.E0)/Eph[i],dSig)
    ##            plt.plot((Ee),dSig)
                tt_=xox.xxCumTrapz(Ee,dSig)
                Eem_.append(list(Ee))

                tt_/=tt_[-1]
                pdf_.append(list(tt_))
                rc=np.interp((gm_),(tt_),(Ee))
##                rc=np.interp(np.log10(gm_[1:]),np.log10(tt_[1:]),np.log10(Ee[1:]))
##                rc=np.power(10,rc)
##                rc=np.insert(rc,0,0.0)
                if kLog and False:
##                    plt.loglog(tt_,(Ee),'r-o')
##                    plt.loglog(gm_,(rc),'b-+')
                    pass
                else:
##                    plt.semilogy(tt_,(Ee),'r-')
##                    plt.semilogy(gm_,(rc),'b-')
                    pass


                ev_=xox.xxTrapz(gm_,rc)

                Eave.append(ev_)
                vev_=Eph[i]/2 -phis.E0
                dv_=np.abs(vev_-ev_)/ev_
##                print('%f  %f  %12.4e ' % (ev_,vev_,dv_))

            else:
                rc=1.0e-16*np.ones(len(gm_,))
            vv_.append(list(rc))


            pass
##        dm_=np.array(vv_)
##        dm_[:,1:]=np.log10(dm_[:,1:])
##        ss='# Output: distribution  energy of pozitron'
##        if kLog:
##            xox.xWrite3_log('para_log', Eph,gm_,dm_,ss)
##        else:
##
##            xox.xWrite3_lin('para_lin', Eph,gm_,dm_,ss)

##        plt.grid(True)
##        plt.show()

        return np.array(Eem_), np.array(pdf_), np.array(vv_), Eave

##        self.vv_=dm_





if __name__ == '__main__':
    Eph_ = np.logspace(2, 8, 25)
    Eph_ = np.array([1.5, 2, 3, 4,  5, 7, 10])*1.e+6
    Eph_ = Eph_[Eph_ > 2 * phis.E0]
##    Eph = [2.1, 2.5, 3., 3.5, 5., 10, 20]
##    Eph_ = np.array(Eph)*phis.E0
    kLog_ = 1
    nG_para = 10
    if kLog_:
        gm = np.logspace(-12, 0, 2**nG_para-1)
        gm = np.insert(gm, 0, 0.0)
    else:
        gm = np.linspace(0., 1., 2**nG_para)
##    gm_=np.logspace(-12,0,2**10)
##    fig1 = plt.figure( 1, figsize=(9,6))
##    fig1.subplots_adjust(right=0.7)
##    ax=fig1.add_subplot(111)
##    p=r'$E_{e^+}, eV$'
##    ax.set_ylabel(p, fontsize=14)
##    ax.set_xlabel('$\gamma$',fontsize=14,style='italic', weight = 'bold')
    Elem_ = 26
    para_ = Paraep()
    x_, pdf_, tbl_, Eave_ = para_.calc_table(Elem_, Eph_, gm, kLog = kLog_)
    fig_ = 1
##    xxp.xtable_plot(Eph_, gm, tbl_, fig_, bxlog = True, bylog = True,
##                ylabel = r'$E_{e^+}, eV$', xlabel = r'$\gamma$' )

    xxp.xtable_plot(Eph_, gm, tbl_, fig_, bxlog = True, bylog = True,
                ylabel = r'$\epsilon_{e^+}, эВ$', xlabel = r'$\gamma$' )
    xxp.xsave_fig(str(Elem_) + '_para_table')

##    for i, ee_ in enumerate(Eph_):
####        sl_ = '%5.2E eV' % (ee_)
##        sl_ = xox.xxformat(ee_)
##        ax.semilogy(gm, tbl_[i], '-', linewidth = 2.0, label =sl_,)
##    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
##    ax.grid(True)
##    plt.ylim(1.e+2, Eph_[-1])
    pass
##    opis_ = {}
##    opis_ = {'legenda':(u'Средняя энергия позитрона',),
##     'ylabel':r'$\widehat{E_{e^+}}, eV$', 'bxlog': True,
##     'bylog':True, 'xlabel':r'$E_{\gamma}, eV$', 'place':'upper left'}
    opis_ = {'legenda':('Средняя энергия позитрона',),
     'ylabel':r'$\widehat{\epsilon_{e^+}}, эВ$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$epsilon_{\gamma}, эВ$', 'place':'upper left'}
    ifig_ =2
    xxp.xgraf_plot(Eph_, Eave_, ifig_, opis_)
    xxp.xsave_fig(str(Elem_) + '_para_average')
    xxp.xshw()
