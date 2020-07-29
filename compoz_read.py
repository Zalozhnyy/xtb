# -*- coding: utf-8 -*-
# !/usr/bin/env python
# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      PC
#
# Created:     13.12.2018
# Copyright:   (c) PC 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------

import os
import sys
import json
import yaml
import numpy as np


def read_elements(ss):
    with open(os.path.join(ss, 'elements.csv'), 'rt') as xfl:
        be = {}
        xfl.readline()
        for line in xfl:
            t = line.split()
            be[int(t[0])] = [t[1], float(t[2]), float(t[3])]
    sn = {}
    for k in list(be.keys()):
        sn[be[k][0]] = int(k)
    return (be, sn)


def read_comp(file_name, el_name):
    """
    """

    dm = {}
    try:
        ff = yaml.load(open(file_name))
    except IOError:
        print(('{0} не существует'.format(file_name)))
        exit(2)
        ##    for ky in sorted(ff.keys()):
        ##        ne_ = len(ff[ky]['elem'])
        ##        em = []
        ##        for el in range(ne_):
        ##            lem = ff[ky]['elem'][el]
        ##            em.append({'el':lem[0], 'A':'{:03d}'.format(lem[1]), 'p':lem[2]})
        ##        ns_ = len(ff[ky]['slice'])
        ls = []
        ##        for sl in range(ns_):
        ##            nmsl = ff[ky]['slice'][sl]
        ##            ls.append(nmsl)
        dm[ky] = {'elem': em, 'slice': ls}

    return ff


def read_comp(file_name):
    """
    """

    ##    dm = {}
    try:
        ff = yaml.load(open(file_name))
    except IOError:
        print(('{0} не существует'.format(file_name)))
        exit(2)
    ##    for ky in sorted(ff.keys()):
    ##        ne_ = len(ff[ky]['elem'])
    ##        em = []
    ##        for el in range(ne_):
    ##            lem = ff[ky]['elem'][el]
    ##            em.append({'el':lem[0], 'A':'{:03d}'.format(lem[1]), 'p':lem[2]})
    ##        ns_ = len(ff[ky]['slice'])
    ##        ls = []
    ##        for sl in range(ns_):
    ##            nmsl = ff[ky]['slice'][sl]
    ##            ls.append(nmsl)
    ##        dm[ky] = {'elem':em, 'slice':ls}

    return ff


def read_mat(nFile, mess={}):
    vt = {}
    em = []
    mp = 0.0
    try:
        with open(nFile, 'rt') as fIn:
            for line in fIn:
                if len(line) < 5:
                    break
                tt = line.split()

                if tt[0].find('Composite') > 0:
                    name = tt[1]
                elif tt[0].find('Element') > 0:
                    pp = float(tt[2])
                    mp += pp
                    if len(tt) == 3:
                        em.append([tt[1], pp])
                    elif len(tt) == 4:
                        em.append([tt[1], pp, int(tt[3])])
                elif tt[0].find('Density') > 0:
                    ro = float(tt[1])
                else:
                    break
            vt = {name: {'elem': em, 'ro': ro}}
            if abs(1.0 - mp) > 1.e-4:
                mess['mes'] = 'Неверно заданы массовые доли композита {0}. Сумма равна {1}'.format(name, mp)
                mess['sum'] = mp
    except IOError:
        mess['mes'] = 'Oтсутствует файл c описанием композита - {0}. '.format(nFile)

    ##    print('point 1')
    return vt


def dump_mat(vt):
    """
    """
    ss = ''
    name = list(vt.keys())[0]
    ss += 'Наименование: ' + name + '\n'
    tv = vt[name]
    ro = str(tv['ro'])
    ss += 'Плотность: ' + ro + '\n'
    ss += 'Элементы:' + '\n'
    for nm, pp in tv['elem']:
        ss += '' + nm + ' - ' + str(pp) + '\n'

    return ss


## Класс для работы с входной информацией о композитах
class Compozit():
    """
    """

    ## Программа дла считывания информации о композитах
    def __init__(self, nFile, nmEl):
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
                        if t[1] in nmEl.keys():
                            sn_ = t[1]
                        else:
                            sn_ = ''
                            print(u'В композите  %s - элемент %s ошибочен.' % (env, t[1]))
                        vs_ = float(t[2])
                        ss_ += vs_
                        ion_ = 0
                        if len(t) > 3:
                            t3 = int(t[3])
                            if t3 <= 2 and t3 > 0:
                                ion_ = t3
                        Mt.append([sn_, vs_, ion_])
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
                        print(('Неверно заданы массовые доли композита {0}. Сумма равна {1}'.format(mt[k]['Composite'],
                                                                                                    ss_)))
        except IOError:
            print(('Oтсутствует файл c описанием композита - {0}. '.format(nFile)))
            exit(2)

    pass

    def conver(self):
        cp = {}
        for elem in sorted(self._vv):
            elm = elem[list(elem.keys())[0]]
            name = elm['Composite']
            cp[name] = {'elem': elm['Element'], 'ro': elm['Density']}

        return cp

    def write_file_yaml(self, nfl):
        with open(nfl, 'w') as ff:
            ff.write(yaml.dump(self.conver()))

    def write_file(self, nfl):
        comp = self.conver()
        with open(nfl, 'w') as ff:
            for cp in sorted(comp.keys()):
                ff.write('[Composite]\t%s\n' % cp)
                for el in comp[cp]['elem']:
                    ff.write('[Element]\t%s\t%f\n' % (el[0], el[1]))
                ff.write('[Density]\t%f\n' % comp[cp]['ro'])
                ff.write('\n')


def write_file_yaml(nfl, dmt):
    with open(nfl, 'w') as ff:
        ff.write(yaml.dump(dmt))


def write_file(nfl, comp):
    ##    comp = self.conver()
    with open(nfl, 'w') as ff:
        for cp in sorted(comp.keys()):
            ff.write('[Composite]\t%s\n' % cp)
            for el in comp[cp]['elem']:
                if len(el) == 3:
                    ff.write('[Element]\t%s\t%f\t%d\n' % (el[0], el[1], el[2]))
                else:
                    ff.write('[Element]\t%s\t%f\n' % (el[0], el[1]) )
            ff.write('[Density]\t%f\n' % comp[cp]['ro'])


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
        print(("такого файла наверное нет.\n%s" % nf))
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

    lm = list(zip(nl, nv, rv))
    d = defaultdict(list)
    for nl, nv, rv in lm:
        d[(nv, rv)].append(nl)

    for ky in list(d.keys()):
        d[ky] = sorted(d[ky])
    if save:
        tt = os.path.split(nf)
        nl = os.path.splitext(tt[1])[0]
        print(nl)
        fn = os.path.join(tt[0], nl + '.yml')
        with open(fn, 'w') as ff:
            ff.write(yaml.dump(dict(d), default_flow_style=False, ))

    return d


def main():
    pass


if __name__ == '__main__':
    sd = os.getcwd()
    ##    tb = read_comp(os.path.join(sd, 'amg.yml'))
    bb = {'sum': '___'}
    tt = read_mat(os.path.join(sd, 'mat_files', 'composite.mrat'), mess=bb)
    s = dump_mat(tt)
    print(s)
    exit(0)
    dd = read_layer(sd)

    print(dd)
    dnb, snb = read_elements(sd)
    cmt = Compozit(os.path.join(sd, 'compozits'), snb)
    cmt.write_file(os.path.join(sd, 'compa'))
    exit(0)
    cmt.write_file(os.path.join(sd, 'assa.yml'))

    eel = cmt.conver()
    cym = read_comp(os.path.join(sd, 'complex.yml'), snb)
    main()
