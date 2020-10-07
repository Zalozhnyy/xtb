# -*- coding: utf-8 -*-
# !/usr/bin/env python
# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Kellinn
#
# Created:     26.09.2020
# Copyright:   (c) Kellinn 2020
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import os
import sys
import yaml
import zipfile as z
import numpy as np

s_templ = "FBB_P_"

head = """Сила торможения протонов в {0:s}
Число строк данных
 {1:d}

Энергия(MeV) Торм полн(MeV/см)
"""


def read_el(dr):
    """
        считываем БД по элементам
        лежит в /DATA /elements.dict
    """
    import csv
    print('read_el')
    elm = {}
    eln = {}

    with open(os.path.join(dr, 'elements.csv'), "r") as flf:
        rr = csv.DictReader(flf, delimiter='\t')
        for rw in rr:
            elm[rw['El']] = {'NN': int(rw['NN']), 'Ro': rw['Ro'], 'A': rw['A']}
        ##            eln[int(rw['NN'])] = {'name':rw['El'],'Ro':rw['Ro'], 'A':rw['A']}

        pass

    return elm


def read_nist(sf):
    """
    """
    sf = str(sf, encoding='utf-8')
    sf = sf.split('\n')
    vf = sf[10:]
    vv = []
    for ls in vf:
        tt = list(map(float, ls.split()))
        if len(tt) > 0:
            vv.append(tt)

    return np.array(vv)


def read_lib(dr, fl_nist, ptkl='p', proc=['NIST', 'NUCLEAR'], ):
    """
        Программа получения тормозных способностей для химических элементов
        Требует  /DATA/stpw-p.zip, /DATA/stpw-a.zip, /DATA/el_z.txt
    """
    nmflzip = 'stpw-' + ptkl + '.zip'
    nff = dr
    en = []

    nmflzip = os.path.join(nff, nmflzip)

    if z.is_zipfile(nmflzip):

        fl_ = z.ZipFile(nmflzip)

        sf = fl_.read('el_z.txt')
        et = str(sf, encoding='utf-8').split('\n')
        en = list(map(int, et))

        if fl_nist > en[-1]: fl_nist = en[-1]

        if fl_nist in en:
            try:
                sf = fl_.read(str(fl_nist))
                fl_.close()
                v_nist = read_nist(sf)
                return v_nist

            except KeyError:
                print(u'Проблема c данными')
                exit(3)
        else:
            for i, n1 in enumerate(en[0:-1]):
                dn1 = fl_nist - n1
                dn2 = fl_nist - en[i + 1]
                tt = dn1 * dn2
                ##                    print(tt)
                if tt < 0:
                    n2 = en[i + 1]
                    break
            sf1 = fl_.read(str(n1))
            sf2 = fl_.read(str(n2))
            fl_.close()
            dn = float(n2 - n1)
            dv = dn1 / dn
            ##                    dn2 *= -1
            ##                    dv2 = dn2 / dn
            v1 = read_nist(sf1)[:, 0:4]
            v2 = read_nist(sf2)[:, 0:4]
            v = v2 * (1.0 - dv) + v1 * dv
            return v


## Класс для работы с входной информацией о композитах
class Compozit():
    """
    """

    ## Программа дла считывания информации о композитах
    def __init__(self, nFile):
        self._vv = []

        i = -1
        env = ''
        ##        vt_={}
        try:
            with open(nFile, 'r') as fIn:
                for k, line in enumerate(fIn):
                    if line.startswith('[' + 'Composite' + ']'):
                        if i > -1:
                            vt_ = {ip: {"Composite": env, "Density": Ro, "Element": Mt, "Shell": Sh}}
                            self._vv.append(vt_)

                        i += 1
                        vt_ = {}
                        Mt = []
                        Sh = []
                        t = line.split()
                        env = t[1]
                        ip = i
                        ss_ = 0
                    ##                    self.vv[env]=i
                    elif line.startswith('[' + 'Element' + ']'):
                        t = line.split()
                        vs_ = float(t[2])
                        ss_ += vs_
                        Mt.append([t[1], vs_])
                    elif line.startswith('[' + 'Shell' + ']'):
                        t = line.split()
                        Sh.append((int(t[1]), ip, t[2]))
                    elif line.startswith('[' + 'Density' + ']'):
                        t = line.split()
                        Ro = float(t[1])
                    elif line.startswith('[' + 'OUtfile' + ']'):
                        t = line.split()
                        self.OutName = (t[1])
                vt_ = {ip: {"Composite": env, "Density": Ro, "Element": Mt, "Shell": Sh}}
                self._vv.append(vt_)
                for k, mt in enumerate(self._vv):
                    vv_ = mt[k]['Element']
                    ss_ = 0
                    for l, ve_ in enumerate(vv_):
                        ss_ += ve_[1]
                    if abs(1.0 - ss_) > 1.e-4:
                        print(u'Неверно заданы массовые доли композита {0}. Сумма равна {1}'.format(mt[k]['Composite'],
                                                                                                    ss_))
                        exit(1)
        except IOError:
            print(u'Oтсутствует файл c описанием композита - {0}. '.format(nFile))
            exit(2)

    pass

    def conver(self):
        cp = {}
        for elem in sorted(self._vv):
            elm = list(elem.keys())
            elm = elem[elm[0]]
            name = elm['Composite']
            cp[name] = {'elem': elm['Element'], 'ro': elm['Density']}

        return cp


def read_layer(ss, nmfl='layers', save=False):
    """
    """
    from collections import defaultdict
    ##    nmfl = 'layers'
    nf = os.path.join(ss, nmfl)
    if len(nmfl) == 0:
        nf = ss
    try:
        with open(nf) as ff:
            lfn = ff.readlines()
    except IOError:
        print(u"такого файла наверное нет.\n%s" % nf)
        return {}
    ##        exit(-1)
    nl = []
    nv = []
    rv = []
    for lr in lfn:
        lr = lr.split()
        if len(lr) < 3:
            continue
        nl.append(int(lr[0]))
        ss_ = lr[1].lower()  # very important
        if sys.version_info.major < 3:
            ss_ = ss_.decode('cp1251') if type(ss_) == type('') else ss_
        nv.append(ss_)
        rv.append(float(lr[2]))

    lm = zip(nl, nv, rv)
    d = defaultdict(list)
    for nl, nv, rv in lm:
        d[(nv, rv)].append(nl)

    for ky in d.keys():
        d[ky] = sorted(d[ky])
    if save:
        tt = os.path.split(nf)
        nl = os.path.splitext(tt[1])[0]
        print(nl)
        fn = os.path.join(tt[0], nl + '.yml')
        with open(fn, 'w') as ff:
            ff.write(yaml.dump(dict(d), default_flow_style=False, ))

    return d


def make_prtk_prt(spr, sly):
    """
        sly - полное имя файла со слоями
        spr - полное имя файла *.prj
    """
    sp_ = os.path.dirname(__file__)
    sb_ = os.path.dirname(spr)
    elx = read_el(sp_)
    drmat = os.path.join(sp_, 'mat_files')
    nmflzip = 'stpw-p.zip'
    nmflzip = os.path.join(sp_, nmflzip)

    if z.is_zipfile(nmflzip):
        fl_ = z.ZipFile(nmflzip)

        sf = fl_.read('energy.txt')
        et = str(sf, encoding='utf-8').split('\n')
        ehp = list(map(float, et))

    sb = os.path.dirname(spr)

    dly = read_layer(sly, nmfl='')
    for mat_, ro in dly.keys():
        st_pow_ = np.zeros((len(ehp),))
        mt = mat_.upper()
        lmat = dly[(mat_, ro)]
        print(mat_, ro)

        fmt = os.path.join(drmat, mat_.lower() + '.mrat')
        print(fmt)
        comp = Compozit(fmt)
        ev = comp.conver()

        for it_, tt in enumerate(ev[list(ev.keys())[0]]['elem']):
            ##            am += int(tt['A']) * tt['p']
            print(tt)
            nme = tt[0]
            print(nme)
            num = elx[nme]['NN']
            vv = read_lib(sp_, num, )
            sx = np.interp(ehp, vv[:, 0], vv[:, 3])
            st_pow_ += tt[1] * sx

        for nmb in lmat:

            sfl = s_templ + '{0:03d}'.format(nmb)

            fot = os.path.join(sb_, sfl)
            with open(fot, 'w') as fotf:
                fotf.write(head.format(mat_, len(ehp)))
                tt = zip(ehp, ro * st_pow_)
                for ee, sv in tt:
                    fotf.write('{0:e}\t{1:e}\n'.format(ee, sv))
    pass


if __name__ == '__main__':
    file_name = os.path.join(os.path.dirname(__file__), 'parameters.yml')
    bd = yaml.load(open(file_name, 'r'), Loader=yaml.FullLoader)
    bd['prj'] = 'c:\\projects\\Sphere\\SPHERE.PRJ'
    bd['lay'] = 'c:\\projects\\Sphere\\SPHERE.LTB'
    make_prtk_prt(bd['prj'], bd['lay'])
