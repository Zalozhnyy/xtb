# -*- coding: utf-8 -*-
# !/usr/bin/env python
## @package endf
# Данный модуль предназначен для работы с ENDF файлами для фотонов и электронов.
#       В данном модуле определены функции для считывания данных из ENDF файлов и
#       определены классы в которых сохраняется информация из ENDF файлов и определены некоторые
#       методы для работы с данными


import re
import os
import sys
import math
import zipfile as z
import math

from scipy import integrate

import numpy as np
from kiadf import phisconst as phis
from kiadf import ion_pkl as ionp

try:
    import matplotlib.pyplot as plt
except:
    xGraff = False
else:
    xGraff = True
    from matplotlib import rc

    font = {'family': 'Verdana',
            'weight': 'normal'}
    rc('font', **font)

from kiadf import xxplot as xxp

TypeParticle = []


def InitElement(name):
    """
    Initialize the initial data for elements
    """
    with open(name, 'rt') as xFl:
        bE = {}
        sN = {}
        d = {}
        for line in xFl:
            t = line.split()
            ##            bE[int(t[0])]=[(chr(int(t[1]))+chr(int(t[2]))).strip(),float(t[3]),float(t[4])]
            bE[int(t[0])] = [t[1], float(t[2]), float(t[3])]
    for k in list(bE.keys()):
        sN[bE[k][0]] = int(k)
    return (bE, sN)


def xcumtrapz(yt_, xt_):
    """ """
    tt_ = (np.trapz(yt_[j:j + 2], xt_[j:j + 2]) for j, x in enumerate(xt_[:-1]))
    ss_ = np.cumsum(np.fromiter(tt_, np.float))
    ss_ = np.insert(ss_, 0, 0.0)
    return ss_


## Вычисляем среднее значение

def xcalcvave(y_, x_):
    """
        вычисляем среднее значение
    """
    return x_[-1] * np.trapz(y_, x_) - np.trapz(xcumtrapz(y_, x_), x_)


## вычисляем среднее значение по нормированному распределению

def xcalc_eave_F(F_, x_):
    """
     """
    return x_[-1] - np.trapz(F_, x_)


## вычисляем среднее значение по нормированному распределению

def xcalc_eave_f(f_, gamma_):
    """
     """
    return np.trapz(f_, gamma_)


## Используется для считывания данных из ENDF файла
#
def GetDummy(MF, MT):
    """
    """
    if MF in (23, 27):
        return 1
    elif MF == 26 and MT != 528:
        return 5
    elif MF == 26 and MT == 528:
        return 4


##  Предназначена для перевода формата ENDF файла в стандартный числовой формат
# Например
#        2.3456986+4 -> 2.3456986E+4
#        2.3456986-3 -> 2.3456986E-3
#        1.345698-13 -> 2.345698E-13
#

def gavno2num(ss):
    ss = ss[::-1]
    p = re.compile('[+-]')
    m = p.search(ss)
    bg = m.start()
    num = ss[0:bg + 1] + "E" + ss[bg + 1:]
    num = num[::-1]
    return num


##Считывает заголовок ENDF файла

def e_head(sf):
    i = 4
    tp = int(sf[i][49:59])
    i += tp + 1
    # nRows=2
    s = sf[i]
    mfC = int(s[29:39])
    mtC = int(s[39:49])
    nRow = int(s[49:59])
    nRows = 2;
    MF = 0
    ret = []
    Shell = []
    while mfC != 0:
        nRows = nRows + (nRow + 0)
        i += 1
        s = sf[i]
        mfC = int(s[29:39])
        mtC = int(s[39:49])
        nRow = int(s[49:59]) + 1
        ret.append([mfC, mtC, nRow, nRows])
        if mfC == 23 and mtC >= 534: Shell.append(mtC)
        if MF != mfC:
            MF = mfC
            ret[-1][3] += 1
            nRows = nRows + 1
    del ret[-1]
    D = {}
    for k in range(len(ret)):
        D[(ret[k][0]), (ret[k][1])] = [ret[k][2], ret[k][3]]

    # input.close()
    return (D, Shell)


def read_endf(sf_, pp_, mfmt_):
    """
    Middle read data from endf file
    """
    mf_ = mfmt_[0]
    mt_ = mfmt_[1]
    # print self.Z,mf,mt
    if mf_ == 23 or mf_ == 27 or mt_ == 528:
        dr_ = read_endf_1d(sf_, pp_, mf_, mt_)
    else:
        dr_ = read_endf_2d(sf_, pp_, mf_, mt_)
    return dr_


def read_endf_1d(sf, pp, mf, mt):
    """
    Reading 0ne-dimensional data from ENDF-file

    For electron:

    23526   Elastic Scattering Cross Sections
    23527   Bremsstrahlung Cross Sections
    23528   Excitation Cross Sections
    23534 ...  Electroionization Subshell Cross Sections
=================================================================

    For photon:
    23501   Total cross sections
    23502   Coherent scattering cross sections
    23504   Incoherent scattering cross sections
    23516   Pair production cross sections, Total
    27502   Coherent scattering form factors
    27504   Incoherent scattering functions
=================================================================

    """

    ng = 11
    res = []
    ShellEb = []
    k = pp[(mf, mt)][1]
    k += GetDummy(mf, mt)
    ss = sf[k]
    nk = int(ss[55:66])
    nrow = int(nk / 3);
    npurga = int((nk - nrow * 3) / 1)
    k += 1

    el = [];
    fl = []
    for i in range(nrow):
        k += 1
        ss = sf[k]
        for j in range(0, 3):
            e = gavno2num(ss[2 * ng * j:ng * (2 * j + 1)]);
            el.append(e)
            f = gavno2num(ss[ng * (2 * j + 1):2 * ng * (j + 1)]);
            fl.append(f)
    if npurga != 0:
        k += 1
        ss = sf[k]
        ##            if iPrintS:print(ss)
        for j in range(0, npurga):
            e = gavno2num(ss[2 * ng * j:ng * (2 * j + 1)]);
            el.append(e)
            f = gavno2num(ss[ng * (2 * j + 1):2 * ng * (j + 1)]);
            fl.append(f)
    res.append([el, fl])
    return el, fl  # res


##Считывает энергию связи для оболочек атома

def get_endf_Eb(nmElement, pp, mt):
    """

    """

    # global nmIniData
    mf = 23
    iPrint = False
    iPrintS = False
    if iPrint: print((mt, mf))
    with open(nmElement, 'r') as input:
        ng = 11
        k = 0
        res = []
        ShellEb = []
        s = str(mf) + str(mt)
        nStrok = pp[s][1]
        for i in range(nStrok): input.readline()
        dm = GetDummy(mf, mt)
        for i in range(dm): input.readline()
        ss = input.readline()
        if iPrintS: print(ss)
        Eb = (ss[0:12]);
    return Eb


##    Считывает двумерные данные из ENDF-файла
def read_endf_2d(sf, pp, mf, mt):
    """
    Считывает двумерные данные из ENDF-файла
    Для электронов:
    26526   Elastic Scattering Cross Sections
    26527   Bremsstrahlung Cross Sections
    26528   Excitation Cross Sections
    26534 ...   Electroionization Subshell Cross Sections
    """

    # global nmIniData
    iPrint = False
    iPrintS = False
    if iPrint: print((mt, mf))
    ng = 11
    k = 0
    res = []
    ShellEb = []
    Ef = []
    k = pp[(mf, mt)][1]
    k += GetDummy(mf, mt)
    ss = sf[k]
    nE = int(ss[0:11]);
    # only for 527 read data meaning energy loss
    k += 1
    for ie in range(nE):
        ss = sf[k]
        eE = gavno2num(ss[11:23]);
        nk = int(ss[55:66])
        Ef.append([eE, nk])
        # nk=int(ss[0:11]);nm=int(ss[11:23])
        # nk*=nm # This is only for 523 and 528
        nrow = int(nk / 3);
        npurga = int((nk - nrow * 3) / 1);
        el = [];
        fl = []
        for i in range(nrow):
            k += 1
            ss = sf[k]
            if iPrintS: print(ss)
            for j in range(0, 3):
                e = gavno2num(ss[2 * ng * j:ng * (2 * j + 1)]);
                el.append(e)
                f = gavno2num(ss[ng * (2 * j + 1):2 * ng * (j + 1)]);
                fl.append(f)
                # if iPrint:print e,f
                # res.append([pp[k][1], e, f])
        if npurga != 0:
            k += 1
            ss = sf[k]
            for j in range(0, npurga):
                e = gavno2num(ss[2 * ng * j:ng * (2 * j + 1)]);
                el.append(e)
                f = gavno2num(ss[ng * (2 * j + 1) + 1:2 * ng * (j + 1) + 1]);
                fl.append(f)
                # if iPrint:print e,f
        res.append([eE, el, fl])
        k += 1
        ss = sf[k]
    return res


def str2float(vv_):
    """
    """
    for ky in list(vv_.keys()):
        pass


##    Определяем наименование исходного файла
#    по номеру элемента или его наименованию
def name_file(partikle_, Z=0, El=''):
    """
    """
    tt_ = "%03i" % (Z) + "_" + El
    if partikle_.startswith('ph'):
        xfile_ = "photoat-" + tt_ + "_000.endf"
    elif Nm_.startswith('ph'):
        xfile_ = "e-" + tt_ + "_000.endf"
    return xfile_


def load_shell():
    """
    Загружает файл с наименованием оболочек
    """
    tt_ = {}
    sn_ = os.path.split(__file__)[0]
    with open(os.path.join(sn_, 'shell.txt'))as in_:
        for k, line in enumerate(in_):
            ts_ = line.split()
            tt_[int(ts_[0])] = {'short': ts_[1], 'long': ts_[2]}
    return tt_


##    Данный класс предназначен для считывания ENDF файла
#    и хранения их в удобном для использования формате

class Endf():
    """
    """
    elZip_ = "e-ENDF-VII0.endf.zip"
    phZip_ = "photoat-ENDF-VII0.endf.zip"
    _str = {}
    prtkl_ = ""
    sig_ = {}

    ##Определяем наименование исходного ENDF-файла
    # по номеру элемента или его наименованию
    #
    def name_file(self):  # , partikle_, Z=0, sEl=''):
        """
         """
        tt_ = "%03i" % (self._Z) + "_" + self._El
        if self.prtkl_.startswith('ph'):
            xfile_ = "photoat-" + tt_ + "_000.endf"
        elif self.prtkl_.startswith('el'):
            xfile_ = "e-" + tt_ + "_000.endf"
        return xfile_

    ##Инициализация класса путем считывания ENDF-файла
    def __init__(self, nfile='', particl='', sEl='', Z=0, ion=0):

        """
        """
        self.sig_['ph'] = (501, 502, 504, 516, 522)
        self.sig_['el'] = (526, 527, 528)
        print(nfile)
        xdir_ = os.path.dirname(__file__)
        if len(nfile) == 0:
            dZ, dN = InitElement(os.path.join(xdir_, 'elements'))
            if Z <= 0:
                Z = dN[sEl]
            if len(sEl) == 0:
                sEl = dZ[Z][0]

            self._El = sEl
            self._Z = Z
            self.prtkl_ = particl
            nfile = self.name_file()
        else:
            self._El = nfile.split('_')[1]

        if nfile.startswith('e'):
            NmFlZip_ = os.path.join(xdir_, self.elZip_)
            self.prtkl_ = 'el'
        elif nfile.startswith('ph'):
            NmFlZip_ = os.path.join(xdir_, self.phZip_)
            self.prtkl_ = 'ph'
        else:
            exit(4)

        if z.is_zipfile(NmFlZip_):
            fl_ = z.ZipFile(NmFlZip_,'r')
            try:
                sf = fl_.read(nfile)
                fl_.close()
            except KeyError:
                print('Oтсутствует файл элемента {0} в базе данных ENDF.'.format(nfile))
                exit(3)

        sf = str(sf, encoding='utf-8')

        ss_ = sf.split('\n')

        self.endf_A = float(gavno2num(ss_[1].split()[1])) * phis.AEM
        self.hh_, self.ElSh_ = e_head(ss_)  # read head of ENDF-file

        # убираем последнюю оболочку, если считаем ион

        self.sig_shell = {}

        for ky in self.hh_.keys():
            self._str[ky] = read_endf(ss_, self.hh_, ky)
        if ion:
            # print ion, sEl
            ionp.set_ion(ion, self._str, elem=self._El)
        ##        self.str_={ky:read_endf(ss_,pp_,ky) for ky in pp_.keys()}

    ## Выдача данных в старом формате, где числа заданы в виде строк
    # Функция добавлена для совместимости со старыми версиями

    def getVS(self, mft_):
        """
        """
        vv_ = []
        if mft_[0] in (23, 27) or mft_[1] == 528:
            vv_.append([mft_[1], self._str[mft_][0], self._str[mft_][1]])
        else:
            dd_ = self._str[mft_]
            ln_ = len(dd_)
            for i in range(ln_):
                vv_.append([mft_[1], dd_[i][0], dd_[i][1], dd_[i][2]])
        return vv_

    ##Возвращает энергию связи оболочек в атоме
    def getEb(self):
        """
        Возвращает энергию связи
        """
        eb_ = {}
        for mt in self.ElSh_:
            eb_[mt] = (float(self._str[(23, mt)][0][0]))
        return eb_

    def getV(self, mft_):
        """
        """
        dd_ = self._str[mft_]

        if mft_[0] == 26 and mft_[1] != 528:
            ll_ = len(dd_)
            vv_ = []
            for i in range(ll_):
                ee_ = float(dd_[i][0])
                xx_ = [float(tt_) for tt_ in dd_[i][1]]
                yy_ = [float(tt_) for tt_ in dd_[i][2]]
                vv_.append((ee_, xx_, yy_))
        else:
            xx_ = [float(tt_) for tt_ in dd_[0]]
            yy_ = [float(tt_) for tt_ in dd_[1]]
            vv_ = (xx_, yy_)
        return vv_

    ## Функция для двумерных распределений плотность вероятности и средние величины
    #
    def getPDF(self, mft_):
        """

        """
        dd_ = self._str[mft_]

        if mft_[0] == 26 and mft_[1] != 528:
            ll_ = len(dd_)
            ave_ = []
            ee_ = []
            xx_ = []
            yy_ = []
            for i in range(ll_):
                ee_.append(float(dd_[i][0]))
                it_ = (float(tt_) for tt_ in dd_[i][1])
                xx_.append(np.fromiter(it_, np.float))
                it_ = (float(tt_) for tt_ in dd_[i][2])
                yy_.append(np.fromiter(it_, np.float))
                ave_.append(xcalcvave(yy_[-1], xx_[-1]))
            e0_ = np.asarray(ee_)
            return (e0_, xx_, yy_, ave_)
        else:
            it_ = (float(tt_) for tt_ in dd_[0])
            xx_ = (np.fromiter(it_, np.float))
            it_ = (float(tt_) for tt_ in dd_[1])
            yy_ = (np.fromiter(it_, np.float))
            return ([], xx_, yy_)

    def getCDF(self, mft_):
        """
        выводятся данные, заданные в ENDF
        e0_ - энергия налетающей частиц
        xx_ - абцисса функции распределения
        vv_ - ордината функции распределения
        pev_ - среднее по плотности функции распределения
        fev_ - среднее по функции распределения
            """
        dd_ = self._str[mft_]

        if mft_[0] == 26 and mft_[1] != 528:
            ll_ = len(dd_)
            vv_ = []
            ee_ = []
            xx_ = []
            yy_ = []
            pev_ = []
            fev_ = []

            for i in range(ll_):
                ee_.append(float(dd_[i][0]))
                it_ = (float(tt_) for tt_ in dd_[i][1])
                xt_ = np.fromiter(it_, np.float)
                it_ = (float(tt_) for tt_ in dd_[i][2])
                yt_ = np.fromiter(it_, np.float)
                pev_.append(xcalcvave(yt_, xt_))
                ss_ = xcumtrapz(yt_, xt_)
                ##                tt_ = (np.trapz(yt_[j:j+2], xt_[j:j+2]) for j,x in enumerate(xt_[:-1]))
                ##                ss_ = np.cumsum(np.fromiter(tt_, np.float))
                ##                ss_ =np.insert(ss_, 0, 0.0)
                if mft_[1] == 526 and ss_[-1] < 1.:
                    xt_ = np.append(xt_, 1.)
                    ss_ = np.append(ss_, 1.)

                ss_ /= ss_[-1]
                fev_.append(xcalc_eave_f(xt_, ss_))
                vv_.append(ss_)
                if mft_[1] == 526:
                    xt_ += 1.
                xx_.append(xt_)

            e0_ = np.asarray(ee_)
            return (e0_, xx_, vv_, pev_, fev_)
        else:

            return ([])

    def getCDF_interp(self, mft_, gg_):
        """
        интерполирование на заданную сетку по гамме
        """

        if mft_[0] == 26 and mft_[1] != 528:
            uu_ = self.getCDF(mft_)
            vv_ = []
            for i, ie in enumerate(uu_[0]):
                ss_ = np.interp(gg_, uu_[2][i], uu_[1][i])
                vv_.append(ss_)
            return np.array(vv_)
        else:

            return ([])

    def calc_sigma_shell(self, xark=False):
        """
        """
        if self.prtkl_ == 'el' and True:

            ee_ = np.array([])
            for i_, mt_ in enumerate(self.ElSh_):
                tt_ = self.getV((23, mt_))
                ee_ = np.union1d(ee_, tt_[0])
            Sig522_ = np.zeros_like(ee_)
            eel_ = np.log10(ee_)
            for i_, mt_ in enumerate(self.ElSh_):
                tt_ = self.getV((23, mt_))
                tt_[1][0] = 10. ** (-16)  # very importatnt, change 0
                tt_ = np.log10(tt_)
                ip_ = eel_ < tt_[0][0]

                ss_ = np.interp(eel_, tt_[0], tt_[1], left=-16.)
                ss_ = np.power(10., ss_)
                ss_[ip_] = 0.
                if xark:
                    self.sig_shell[mt_] = ss_
                Sig522_ += ss_
            return (ee_, Sig522_)

    def calc_sigma_xark(self, xrk_=0):
        """
        """
        if self.prtkl_ == 'el' and True:
            sh_ = []
            ee_ = np.array([])
            for i_, mt_ in enumerate(self.ElSh_):
                tt_ = self.getV((23, mt_))
                ee_ = np.union1d(ee_, tt_[0])
            Sig522_ = np.zeros_like(ee_)
            eel_ = np.log10(ee_)
            for i_, mt_ in enumerate(self.ElSh_):
                tt_ = self.getV((23, mt_))
                tt_[0][1] = 10. ** (-16)
                tt_ = np.log10(tt_)
                ip_ = eel_ < tt_[0][0]

                ss_ = np.interp(eel_, tt_[0], tt_[1], left=-16.)
                ss_ = np.power(10., ss_)
                ss_[ip_] = 0.
                self.sig_shell[mt_] = ss_
                Sig522_ += ss_
            return (ee_, Sig522_)

    def calc_sigma_all(self):
        """
        """
        if self.prtkl_ == 'el' and True:
            tt_ = self.calc_sigma_shell()
            ee_ = tt_[0]
            for i_, mt_ in enumerate(phis.sig_[self.prtkl_]):
                tt_ = self.getV((23, mt_))
                ee_ = np.union1d(ee_, tt_[0])
            SigAll_ = np.zeros_like(ee_)
            eel_ = np.log10(ee_)
            for i_, mt_ in enumerate(phis.sig_[self.prtkl_]):
                tt_ = self.getV((23, mt_))
                tt_ = np.log10(tt_)
                ip_ = eel_ < tt_[0][0]

                ss_ = np.interp(eel_, tt_[0], tt_[1], left=-16.)
                ss_ = np.power(10., ss_)
                ss_[ip_] = 0.
                ##                self.sig_shell[mt_]=ss_
                SigAll_ += ss_
            return (ee_, SigAll_)


class Kendf(Endf):
    """
    """

    def __init__(self, nfile='', particl='', sEl='', Z=0, Elog_=[1., 10.], ion=0):
        self.sig_shell = {}
        self.Sigma = {}

        Endf.__init__(self, nfile, particl, sEl, Z, ion)
        self.El_ = np.array(Elog_[:])
        self.calc_sigma_shell()
        self.calc_sigma()

    def calc_sigma_shell(self):
        """
        """
        nd_ = self.El_.shape
        SiAll_ = np.zeros(nd_)
        for i_, mt_ in enumerate(self.ElSh_):
            tt_ = self.getV((23, mt_))
            if self.prtkl_ == 'el':
                tt_[1][0] = 10. ** (-16)
            tt_ = np.log10(tt_)
            ip_ = self.El_ < tt_[0][0]
            ss_ = np.interp(self.El_, tt_[0], tt_[1])
            ss_ = np.power(10., ss_)
            ss_[ip_] = 0.
            self.sig_shell[mt_] = ss_
            SiAll_ += ss_
        self.sig_shell['All'] = SiAll_
        if self.prtkl_ == 'ph' and False:
            tt_ = self.getV((23, 522))
            tt_ = np.log10(tt_)
            ss_ = np.interp(self.El_, tt_[0], tt_[1])
            Sig522_ = np.power(10., ss_)
        pass

        # plt.semilogy(self.El_,Sig522_,'r-o',self.El_,self.sig_shell['All'],'b-+')
        # return self.sig_shell

    def calc_sigma(self):
        """
        """

        if self.prtkl_ == 'ph':
            for mt_ in self.sig_[self.prtkl_]:
                tt_ = self.getV((23, mt_))
                ##            d=[c/self.A for c in self.d]
                # tuta sigma becouse divide A
                if mt_ in (515, 516, 517):
                    tt_[1][0] = 1.e-16
                tt_ = np.log10(tt_)
                uu_ = np.interp(self.El_, tt_[0], tt_[1])
                ##                plt.figure(mt_)
                ##                plt.plot(tt_[0],tt_[1],'r-o',self.El_,uu_,'b-+')
                self.Sigma[mt_] = np.power(10., uu_)
        pass

    def getEb4E(self):
        """
        """
        nd_ = self.El_.shape
        SiEbAll_ = np.zeros(nd_)

        eb_ = self.getEb()

        SiShell_ = []
        for mt_ in self.ElSh_:
            SiEbAll_ += eb_[mt_] * self.sig_shell[mt_]
        i0_ = (self.sig_shell['All'] == 0.0)
        self.sig_shell['All'][i0_] = 1.E-16
        rr_ = SiEbAll_ / self.sig_shell['All']
        # plt.semilogy(self.El_,Sig522_,'r-o')
        return rr_


if __name__ == '__main__':
    ##    sc="2.3456986+4"
    ##    dd=gavno2num(sc)
    ##    print((sc,dd))
    ##    NmFlZip_="photoat-ENDF-VII0.endf.zip"#"e-ENDF-VII0.endf.zip"
    ##    dZ,dN = InitElement('elements')
    pass
