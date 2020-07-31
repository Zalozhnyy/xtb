#!/usr/bin/python
# -*- coding: utf-8 -*-

## @package photon
# Данный модуль предназначен для вычисления таблиц распределений для фотонов.
# В данном модуле определены классы и функции расчета распределений.
#    Готовятся следующие файлы
# - xtbl.23 – массовые сечения для процессов взаимодействия(см2/г)
#   + Полное массовое сечение взаимодействия (см2/г)
#   + Массовое сечение когерентного рассеяния (см2/г)
#   + Массовое сечение Комптоновского рассеяния (см2/г)
#   + Полное массовое сечение рождения пар (см2/г)
#   + Полное массовое сечение фотопоглощения (см2/г)
# - xtbl.iv - таблица для розыгрыша косинуса угла фотона для неупругого рассеяния
# - xtbl.ive - таблица для розыгрыша энергии электрона для неупругого рассеяния
# - xtbl.cv - таблица для розыгрыша косинуса угла фотона для упругого рассеяния
# - xtbl.516   таблица для розыгрыша энергии позитрона при рождении электронно-позитронных пар.


import os
import math
import numpy as np

##try:
##    import matplotlib.pyplot as plt
##
##except:
##    xGraf = False
##else:
##    xGraf = True

xGraf = not False

import xxfun as xox
import interface as xItf
import phisconst as phis
import endf as ken

##import para_photon as par

# modul xxfun.py

lGraf = True


## Функция предназначена вычисления q
#
def qar(ee_, nn_):
    Qmax = phis.Kph / phis.E0 * ee_ * phis.Sq2
    qq_ = np.linspace(0.0, Qmax, nn_)
    xx_ = 1.0 - (phis.E0 * qq_ / phis.Kph / ee_) ** 2
    xx_ = xx_[::-1]
    xx_[0] = -1.0
    xx_[-1] = 1.0
    return qq_, xx_


## Класс используемый для вычисления фотонных распределений
# @param ken.Kendf класс Kendf из endf.py
class photon(ken.Kendf):
    """
     =================================================================2000 1451   15
      MF/MT     Description                                           2000 1451   16
     =================================================================2000 1451   17
      23/501   Total cross sections                                   2000 1451   18
      23/502   Coherent scattering cross sections                     2000 1451   19
      23/504   Incoherent scattering cross sections                   2000 1451   20
      23/515   Pair production cross sections, Electron field         2000 1451   21
      23/516   Pair production cross sections, Total                  2000 1451   22
      23/517   Pair production cross sections, Nuclear field          2000 1451   23
      23/522   Total photoionization cross section                    2000 1451   24
      23/534   K (1S1/2)    Photoionization subshell cross section    2000 1451   25
      -------------------------------------------------------------
      --------------------------------------------------------------
     =================================================================2000 1451   33
      27/502   Coherent scattering form factors                       2000 1451   34
      27/504   Incoherent scattering functions                        2000 1451   35
      27/505   Imaginary anomalous scattering factor                  2000 1451   36
      27/506   Real anomalous scattering factor                       2000 1451   37
     =================================================================2000 1451   38
    """
    nmElData = r"..\initial_data\electrons\endf"
    nmIniData = r"..\initial_data"
    nmOutData = r"..\out\electrons"

    if 1:
        nmElData = r"c:\ENDF\initial_data\photons\endf"
        nmIniData = r"c:\ENDF\initial_data"
        nmOutData = r"c:\ENDF\out\photons\endf"

    L = phis.E0
    K = phis.Kph

    nE = 101;
    Emin = 2;
    Emax = 7;

    ## Функция инициализации класса photon

    def __init__(self, xin):

        self.Z = xin['Z']  # number element
        self.Ro = xin['Ro']
        self.A = xin['A']
        self.Name = xin['Name']
        self.nmIniData = xin['elem_dir_IN']
        self.nmElData = os.path.join(self.nmIniData, r"photons")
        self.nmOutData = os.path.join(xin['elem_dir_OUT'], r"photons")

        self.nG = xin['nG']

        self.Emin = xin['Emin']
        self.Emax = xin['Emax'];
        self.nE = xin['nE']
        ##        self.nE=xin['En']
        self.E_log = xox.xxlinspace(self.Emin, self.Emax, self.nE);
        self.E = [pow(10, c) for c in self.E_log]

        self.G = xox.xxlinspace(0.0, 1.0, self.nG)

        self.nX = xin['nX']  # int(math.pow(2,13))
        self.Qmax = self.K / self.L * self.E[-1] * math.pow(2., 0.5)
        ##        self.q=np.linspace(0.0,self.Qmax,self.nX)
        ##        x=[1-(self.L*c/self.K/self.E[-1])**2 for c in self.q]
        ##        self.X=x[::-1]
        ##        self.X[0]=-1.
        ##        self.X[-1]=1.
        self.q = []
        self.X = []
        for ie, e in enumerate(self.E):
            ##            F=[e*c/self.L for c in self.q]
            qt_, xt_ = qar(e, self.nX)
            self.q.append(qt_)
            self.X.append(xt_)

        self.OutDir = os.path.join(self.nmOutData, self.Name)
        self.OutDirEndf = os.path.join(self.OutDir, 'ENDF')
        self.xfile = "photoat-" + "%03i" % (self.Z) + "_" + self.Name + "_000.endf"

        ken.Kendf.__init__(self, self.xfile, Elog_=self.E_log)

        self.xDirFileElem = os.path.join(self.nmElData, self.xfile)

        # self.nmOutDataElem=nmOutData+self.Name;
        self.xxDir = os.path.join(self.OutDir,
                                  '%i' % (self.E_log[0]) + '_' + '%i' % (self.E_log[-1]) +
                                  '_' + '%i' % (len(self.E_log)) + '_' + '%i' % (self.nG))
        # xox.xxMkDir(self.xxDir);
        self.NameFile = 'ph-' + '%03i' % (self.Z) + '_' + self.Name + '-kiam';
        ##        self.mas,self.Shell_MT=xox.e_head(os.path.join(self.nmElData,self.xfile))
        ##        self.Nshell=len(self.Shell_MT)

        self.El_NameFile_Out = {}  # name file for out for elements
        for k in ('23', 'iv', 'cv', 'riv', 'rcv', 'div', 'dcv', 'eb'):
            self.El_NameFile_Out[k] = os.path.join(self.xxDir, self.NameFile + '.' + k)

    def read_endf(self, mf, mt):
        # print self.Z,mf,mt
        # d=xox.read_endf_1d(self.xDirFileElem,self.mas,mf,mt)
        self.d = self.getVS((mf, mt))
        return self.d

    def get_endf(self, mf, mt):
        # print( self.Z,mf,mt)
        if mf == 23 and mt in (501, 502, 504, 516, 522):
            d = self.read_endf(mf, mt)
            ##            d=[c/self.A for c in self.d]
            # tuta sigma becouse divide A
            ee = [math.log10(float(c)) for c in d[0][1]]
            ff = [(float(c) / self.A) for c in d[0][2]]
            if mt in (515, 516, 517):
                ff[0] = 1.e-16
            ff = [math.log10(c) for c in ff]
            u = xox.xxInterp1(ee[:], ff, self.E_log)
            ip = np.array(self.E_log) < np.array(ee)[0]
            u = np.array(u)
            u[ip] = -16
            u = list(u)


        elif mf == 27 and mt in (502, 504):
            self.d = self.read_endf(mf, mt)
            u = []
            x = [float(c) for c in self.d[0][1]]
            y = [float(c) for c in self.d[0][2]]

            u.append(x)
            u.append(y)
        return u;

    def xox_23(self):
        """
        """
        self.Sigma23 = []
        for mt in (501, 502, 504, 516, 522):
            d = self.get_endf(23, mt)
            self.Sigma23.append(d)
        if False: self.xWrite_23(self.El_NameFile_Out['23'], self.Sigma23)
        Sigma23 = np.array(self.Sigma23)
        ##        Sigma23=[[math.pow(10,self.Sigma23[k][i]) for i in range(len(self.Sigma23[0]))] for k in range(len(self.Sigma23))]
        Sigma23 = np.power(10, Sigma23)
        return Sigma23.transpose()

    def get_endf_shell_23(self):
        """
        self.d_23_666 - the sum of all envelope
        """
        self.d_23_666 = [0.0 for i in range(self.nE)]

        self.mtx = []
        for mt in self.Shell_MT:
            u = self.get_endf_23(23, mt)
            # self.d_23_666=[(u[i]+self.d_23_666[i]) for i in range(self.nE)]
            for i in range(self.nE):
                self.d_23_666[i] += u[i];
            self.mtx.append(u)
        self.mtx.append(self.d_23_666);
        return self.mtx;

    def xWrite_23(self, NameFl, d, acca='full', Density=-1):

        with open(NameFl, 'w')as Out:

            # write heap
            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1'] + '\n') % (self.nE, 6, 2, 16))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE'] + '\n') % (self.Emin, self.Emax, self.nE, 2))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['fInf']))
            if Density < 0:
                Ro = self.Ro
            else:
                Ro = Density
            Out.write((xox.xT['fInf'] + '\n') % (self.Z, self.A, Ro, 10))
            Out.write('{0} \n'.format(xox.xT['sInf']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            sss = """\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - decimal logarithm of Total cross sections per massa(cm^2/gramm)
# 3 column - decimal logarithm of Coherent scattering cross sections per massa(cm^2/gramm)
# 4 column - decimal logarithm of Incoherent scattering cross sections per massa(cm^2/gramm)
# 5 column - decimal logarithm of Total Pair production cross sections per massa (cm^2/gramm)
# 6 column - decimal logarithm of Total photoionization cross section per massa (cm^2/gramm)"""
            Out.write('{0} \n'.format(sss))
            Out.write('{0} \n'.format('6(%+19.15f )'))
            Out.write('{0} \n'.format(xox.xT['sDE']))

            # write data
            for k in range(self.nE):
                sf = ' %+19.15f ' % (self.E_log[k])
                for i in range(5):
                    sf += '%+19.15f ' % (d[i][k])
                sf += '\n';
                Out.write(sf);

    ## Функция для вычисления угловых распределений
    #   - Кляйне-Нишина(Kv=0,1)
    #   - Томсон(Kv=2)

    def xxFactor(self, Kv):
        self.Fm = []
        for i, e in enumerate(self.E):

            # ft=[1.0+e*(1.0-x) for x in self.X]
            x = self.X[i]
            if Kv == 1 or Kv == 0:
                e /= self.L
                F = (1.0 + x ** 2 + (e * (1.0 - x)) ** 2 / (1.0 + e * (1.0 - x))) / (1.0 + e * (1.0 - x)) ** 2
            else:
                F = 1.0 + x ** 2
            self.Fm.append(F)
        self.Fm = np.array(self.Fm)
        return self.Fm

    def Factor_Rv(self, Kv):
        """

        """
        xZero_ = -24
        if Kv == 1:
            z = 'riv'
        elif Kv == 2:
            z = 'rcv'
        self.Rv = []
        xF = []
        mt = 504 if Kv == 1 else 502
        d = self.get_endf(27, mt)
        q_e = np.array(d[0])
        R_e = np.array(d[1])  # /self.Z
        ##        Qx=xox.xxInterp1((q_e),(R_e),(self.q))
        qmin = np.floor(np.log10(q_e[1]))
        qmax = 9.0


        q = np.logspace(qmin, 9, int(10 * (qmax - qmin) + 1))

        q = np.insert(q, 0, 0.0)
        Qx = xox.xxInterp1(np.log10(q_e[1:]), np.log10(R_e[1:]), np.log10(q[1:]))
        Qx = np.power(10, Qx)
        if Kv == 1:
            Qx = np.insert(Qx, 0, 0.0)
        else:
            Qx = np.insert(Qx, 0, self.Z)
        xx_ = np.array(self.X)
        ##        if xGraf:
        ##            kFig=Kv
        ##            self.fig=plt.figure(kFig,figsize=(12,10))
        ##            cx=self.fig.add_subplot(421)
        ##            cx.loglog(R_e,q_e,'b-o',Qx,q,'r-+')
        ##            cx.set_xlabel('FR')
        ####            cx.xaxis.set_ticks([0+0.1*t for t in range(11)])
        ##            cx.set_ylabel('q')
        ##            cx.grid(True)

        ##        if xGraf:
        ##            ax=self.fig.add_subplot(422)
        ##            ax.set_xlabel(r'$cos(\theta)$')
        ##            ax.set_ylabel('q')
        ##            ax.grid(True)
        ##
        ##            bx=self.fig.add_subplot(424)
        ##            bx.set_xlabel(r'$cos(\theta)$')
        ##            bx.set_ylabel('FR')
        ##            bx.grid(True)

        for ie, e in enumerate(self.E):
            ##            F=[e*c/self.L for c in self.q]
            ##            vv_=qar(e,self.nX)
            Rx = np.interp((self.q[ie]), (q[:]), (Qx[:]))

            Rx = Rx[::-1]
            ##            if xGraf:
            ##                ax.semilogy(self.X[ie],self.q[ie][::-1],'-')
            ##
            ##                bx.semilogy(self.X[ie],Rx,'-')

            if Kv == 2:
                Rx = np.power(Rx, Kv)
            ##            print(len(Rx))
            self.Rv.append((Rx))
        ##            xF.append(F)
        s = '# output: distribution for Kv=' + str(Kv)
        ##        self.xWrite_3D(self.El_NameFile_Out[z],self.Rv,s)
        return self.Rv

    def xxDistrb(self, f, r, Kv):
        """
            f-form-factor(Kv=2),function of scattering(Kv=1)
            r-Kline-Nishina(Kv=1), Tomson(Kv=2)
        """
        R = []
        Rv = []
        fM = []
        dM = []
        fF = []

        ##        if xGraf:
        ##            print('show grafics')
        ##            dx=self.fig.add_subplot(426)
        ##            dx.set_xlabel(r'$cos(\theta)$')
        ##            if Kv == 1:
        ##                dx.set_ylabel('KlNi')
        ##            elif Kv == 2:
        ##                dx.set_ylabel('Tomson')
        ##            dx.grid(True)
        ##            gx=self.fig.add_subplot(428)
        ##            gx.set_xlabel(r'$cos(\theta)$')
        ##            gx.set_ylabel('distr')
        ##            gx.grid(True)

        for k in range(self.nE):

            if Kv == 1 or Kv == 0:
                z = 'iv'
                zd = 'div'
                F = f[k, :] * r[k, :]
                fF.append(F / np.max(F))
            ##                F=1*r[k,:]

            else:
                z = 'cv'
                zd = 'dcv'
                F = f[k, :] * r[k, :]
            ##            if xGraf:
            ##                dx.semilogy(self.X[k],r[k,:],'-')
            ##                gx.semilogy(self.X[k],F,'-')

            sF = xox.xxCumTrapz(self.X[k], F)
            # plt.semilogy(self.X,f[k,:],'r-+',self.X,r[k,:],'b-*' ,self.X,F,'k-o')
            ##                plt.plot((self.X),np.transpose(fF))
            SS = sF[-1]
            cP = [c / SS for c in sF]
            ##            fM.append(xox.xxTrapz(self.G,D))
            D = np.interp(self.G, cP, self.X[k])
            fM.append(xox.xxTrapz(self.G, D))
            ##            dM.append(1-xox.xxTrapz(self.X[k],cP))
            R.append(D)
            Rv.append(cP)
        # self.R=xox.xxTrans(R)
        ##        c
        ##        plt.plot(self.X,np.transpose(Rv)) # plt.plot(np.transpose(self.X),np.transpose(Rv),'-+')
        self.R = R
        self.Rv = Rv
        ##        plt.plot((self.X),np.transpose(fF))
        s = '# output: distribution for Kv=' + str(Kv)
        ##        self.xWrite_3D(self.El_NameFile_Out[zd],self.Rv,s)
        s = '# output: table(gamma) for Kv=' + str(Kv)
        ##        self.xWrite_3D(self.El_NameFile_Out[z],self.R,s)
        self.Rv = np.array(self.Rv)
        return self.Rv

    def xWrite_3D(self, NameFl, d, sss, acca='full'):
        """ write 3D data"""
        nCol = len(d)
        nRow = len(d[0])
        with open(NameFl, 'w') as Out:
            # write heap
            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1'] + '\n') % (nRow, nCol, 2, 8))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE'] + '\n') % (self.Emin, self.Emax, self.nE, 5))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+19.15f )\n'.format(nCol))
            Out.write('{0} \n'.format(xox.xT['sDE']))
            for k in range(nRow):
                sf = '';  # str();
                for i in range(nCol):
                    sf += '%+19.15E ' % (d[i][k])
                sf += '\n';
                Out.write(sf);

    def xWrite_DE(self, nameFL, e, d, sss, acca='full'):
        """ write 2D data"""
        nc = sss.count('\n') - 1
        d.insert(0, e)
        ln = len(d)
        le = len(e)
        with open(nameFL, 'w') as Out:
            # write heap

            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1'] + '\n') % (le, ln, 2, nc + 9))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE'] + '\n') % (e[0], e[-1], le, nc + 6))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%%+19.15f )\n'.format(ln))
            Out.write('{0} \n'.format(xox.xT['sDE']))

            # write data
            for k in range(le):
                sf = ''
                for i in range(ln):
                    sf += '%+19.15f ' % (d[i][k])
                sf += '\n'
                Out.write(sf)

    def xWrite_DE_1(self, nameFL, e, d, sss, acca='full'):
        """ write 1D data"""
        nc = sss.count('\n') - 1
        ##        d.insert(0,e)
        ##        d=[e,d]
        ##        d=np.array(d)
        ln = 2
        le = len(e)
        with open(nameFL, 'w') as Out:
            # write heap

            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1'] + '\n') % (le, ln, 2, nc + 9))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE'] + '\n') % (e[0], e[-1], le, nc + 6))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+15.11e )\n'.format(ln))
            Out.write('{0} \n'.format(xox.xT['sDE']))

            # write data
            for k, dv in enumerate(d):
                sf = '%+19.15f %+15.11e\n' % (e[k], dv)
                Out.write(sf)


## Программа для расчета таблиц фотонных распределений для композитов
#
def main(xI, Mt, matFile, path):
    """
    """
    import para_photon as para
    print((os.getcwd()))
    ##    path,nmFile = os.path.split(matFile)
    ##    path = os.getcwd()
    ##    NmFile,ExtFile = os.path.splitext(nmFile)
    NmFile = Mt.NameTable
    #        xI=xItf.xxInit()
    nE = xI.xin['nE']
    #    nE=xI.xin['En']
    nG = xI.xin['nG']
    nX = xI.xin['nX']
    ##    nX = xI.xin['nG']
    nG_para = xI.xin['nG_para']

    d_sig = np.zeros((nE, 5))
    d_rv1 = np.zeros((nE, nX))  # incoherent
    d_rv2 = np.zeros((nE, nX))  # coherent

    d_eb = np.zeros((nE,))
    #        matFile=os.path.join(path,nfile)
    #        Mt=xItf.Material(matFile)
    #        NmFile,ExtFile=os.path.splitext(nfile)
    DirOut = os.path.join(path, Mt.OutName, 'photon')
    xox.xxMkDir(DirOut)
    FileOut = os.path.join(DirOut, NmFile) + '.'
    spisok = Mt.Mat
    S = 0
    Emin = xI.xin['Emin']
    Emax = xI.xin['Emax'];
    nE = xI.xin['nE']
    #        self.nE=xin['En']
    Eph_ = np.logspace(Emin, Emax, nE);

    gm_para = np.logspace(-12, 0., nG_para - 1)
    gm_para = np.insert(gm_para, 0, 0.0)
    iEph_ = Eph_ > 2 * phis.E0
    Eph_ = Eph_[iEph_]
    nP = len(Eph_)
    iPara_ = False
    if nP > 0:
        iPara_ = True
    #        d_para=np.zeros((nE,nP)) #para produced
    for i, k in enumerate(spisok):
        #            p=Mt.Mat[k]
        name = k[0]
        p = k[1]

        xB = xI.def_element(name)
        #        Elem=xPh.photon(xB)
        Elem = photon(xB)

        r1 = Elem.xxFactor(1)
        r2 = Elem.xxFactor(2)

        Sig = Elem.xox_23()
        d_sig += p * Sig

        sig_rv1 = Sig[:, 2]
        sig_rv1 = np.tile(sig_rv1, (nX, 1))
        sig_rv1 = sig_rv1.transpose()

        sig_rv2 = Sig[:, 1]
        sig_rv2 = np.tile(sig_rv2, (nX, 1))
        sig_rv2 = sig_rv2.transpose()

        if iPara_:
            # para produced
            para_ = para.Paraep()
            x_, pdf_, tbl_, Eave_ = para_.calc_table(Elem.Z, Eph_, gm_para, kLog=1)
            if i == 0:
                d_para = np.zeros(pdf_.shape)  # para produced

            sig_para = Sig[:, 3]
            sig_para = sig_para[iEph_]
            sig_para = np.tile(sig_para, (nG_para, 1))
            sig_para = sig_para.transpose()
            d_para += p * sig_para * pdf_

        sig_photo = Sig[:, 4]

        eb_ = Elem.getEb4E()
        d_eb += p * eb_ * sig_photo

        d1 = Elem.Factor_Rv(1)
        d1 = np.array(d1)
        t1 = Elem.xxDistrb(d1, r1, 1)
        d_rv1 += p * sig_rv1 * t1

        d2 = Elem.Factor_Rv(2)
        d2 = np.array(d2)
        t2 = Elem.xxDistrb(d2, r2, 2)
        d_rv2 += p * sig_rv2 * t2
        print(name)
    # -------------------------------------------------------------------------------

    e = Elem.E_log
    X = np.array(Elem.X)
    G = np.array(Elem.G)
    sig_coh = d_sig[:, 1]
    sig_coh = np.tile(d_sig[:, 1], (nX, 1))
    sig_coh = sig_coh.transpose()
    sig_inc = d_sig[:, 2]
    sig_inc = np.tile(d_sig[:, 2], (nX, 1))
    sig_inc = sig_inc.transpose()
    d_rv1 /= sig_inc
    d_rv2 /= sig_coh
    if iPara_:
        sum_sig_para = d_sig[iEph_, 3]
        sum_sig_para = np.tile(sum_sig_para, (nG_para, 1))
        sum_sig_para = sum_sig_para.transpose()
        d_para /= sum_sig_para

    Sig_Out = list(np.log10(d_sig.transpose()))
    Elem.xWrite_23(FileOut + '23', Sig_Out, Density=Mt.Ro)

    D1 = xox.xxGeTablePhoton((d_rv1), X, G)
    s = '# output: distribution cos(tet) for Incoherent scattering (Klein-Nishina)'
    Elem.xWrite_3D(FileOut + 'iv', list(D1), s)

    me_ = np.transpose(np.tile(Elem.E, (len(Elem.G), 1)))
    xx_ = me_ / (1 + me_ * (1 - X) / phis.E0)
    DE = xox.xxGeTablePhoton((d_rv1), xx_, G)
    s = '# output: distribution Energy (eV) for Incoherent scattering (Klein-Nishina)'
    Elem.xWrite_3D(FileOut + 'ive', list(DE), s)

    D2 = xox.xxGeTablePhoton((d_rv2), X, G)
    s = '# output: distribution cos(tet) for Coherent Scattering (Thomson expression)'
    Elem.xWrite_3D(FileOut + 'cv', list(D2), s)

    d_eb /= d_sig[:, 4]
    s = """\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - Binding Energy for photoionization, eV"""

    Elem.xWrite_DE_1(FileOut + 'eb', Elem.E_log, list(d_eb), s)

    D_para = np.ones((Elem.nE, nG_para)) * 1.e-16

    if iPara_:
        for j, k in enumerate(range(Elem.nE - nP, Elem.nE)):
            D_para[k, :] = np.interp((gm_para), (pdf_[j, :]), (x_[j, :]))
    ss = '# Output: distribution decimal logarithm of energy of pozitron'
    D_para[:, 1:] = np.log10(D_para[:, 1:])
    D_para[:, 0] = -16.0
    xox.xWrite3_log(FileOut + '516', Elem.E, gm_para, D_para, ss)
    #        Elem.xWrite_3D(FileOut+'516',list(D_para),s)
    pass


##    if xGraf:
##        plt.show()

if __name__ == '__main__':
    ##    import interface as xItf

    matFile = 'xal.mat'
    xI = xItf.xxInit(nFile='xparameter.ini')
    Obt = xItf.xObject(matFile, xI.sN)
    for k, mt in enumerate(Obt.vv):
        Mt = xItf.Material(mt[k])
        ph_mat(xI, Mt, matFile)
    exit(0)
    Z = 13
    xI = xItf.xxInit()
    xB = xI.def_element(Z=Z)
    A = photon(xB)
    u = A.xox_23()

    A = photon_mat(r'c:\initial_data')
