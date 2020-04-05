# -*- coding: utf-8 -*-
# !/usr/bin/env python
## @package prtk_table
# Данный модуль предназначен для пересчета таблиц во входной формат
# программы переноса РЭМП
# с использованием данных полученных программой по обработке данных ENDF
#   - таблица ионизации атом электроном (.555)
#   - таблица энергии при комптоновском рассеянии (.ive)
#   - таблица торможения электронов (.xer)
#   - таблица энергии вылетевшего фотона при тормозном излучении (.527)
#   - таблица средней энергии связи (.eb)
#   - таблица энергии электрона при рождении электронно-позитронных пар (.516)

import os
import time
import shutil
import glob
##import numpy as np
import yaml
import locale

import compoz_read as cord
import Project_reader

## Функция для считывания материалов, для которых
# необходимо пересчитать таблицы
#

dir_file = 'prtk_files'

prc_ptk = ['ELA', 'EXC', 'ION', 'ROT', 'ATT', 'REC']
prc = ['REC', ]
prc1 = ['REC']


def ff_rec(fl, kf):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return []

    return ls


def ff_ela(fl, kf):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return []
    nn = int(ls[5])
    fs = ls[:10]

    for ll in ls[10:]:
        tt = '{0:13.4e} '.format(float(ll[12:25]) * kf)
        ll = ll[:12] + tt + ll[25:]
        fs.append(ll)

    return fs


def ff_att(fl, kf):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return []
    kf2 = kf * kf
    nb = 8
    na = int(ls[5])
    fs = ls[:nb]

    for i, ll in enumerate(ls[nb:]):
        if i < 35:
            kk = kf2
        else:
            kk = kf

        tt = '{0:13.4e} '.format(float(ll[12:25]) * kk)
        ll = ll[:12] + tt + '\n'
        fs.append(ll)

    return fs


def ff_ion(fl, kf):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return []
    fs = []
    nn = int(ls[4])

    nb = 7
    nh = 8
    fs = ls[:nb]

    for i in range(nn):
        [fs.append(ss) for ss in ls[nb:nb + nh]]
        nl = int(ls[nb + nh - 2])
        for ll in ls[nb + nh:nb + nh + nl]:
            tt = '{0:13.4e} '.format(float(ll[12:25]) * kf)
            ll = ll[:12] + tt + ll[25:]
            fs.append(ll)
        nb += nh + nl

    return fs


def ff_exc(fl, kf):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return []
    fs = []
    nn = int(ls[4])

    nb = 5
    nh = 8
    fs = ls[:nb]

    for i in range(nn):
        [fs.append(ss) for ss in ls[nb:nb + nh]]
        nl = int(ls[nb + nh - 2])
        for ll in ls[nb + nh:nb + nh + nl]:
            tt = '{0:13.4e} '.format(float(ll[12:25]) * kf)
            ll = ll[:12] + tt + ll[25:] + '\n'
            fs.append(ll)
        nb += nh + nl

    return fs


def ff_rot(fl, kf):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return []
    fs = []
    nn = int(ls[3])

    nb = 4
    nh = 6
    fs = ls[:nb]

    for i in range(nn):
        [fs.append(ss) for ss in ls[nb:nb + nh]]
        nl = int(ls[nb + nh - 2])
        for ll in ls[nb + nh:nb + nh + nl]:
            tt = '{0:13.4e} '.format(float(ll[12:25]) * kf)
            ll = ll[:12] + tt + ll[25:]
            fs.append(ll)
        nb += nh + nl

    return fs


prt = {'ELA': ff_ela, 'EXC': ff_exc, 'ION': ff_ion,
       'ROT': ff_rot, 'ATT': ff_att, 'REC': ff_rec}


def read_ro(fl):
    try:
        with open(fl, 'r', encoding='utf-8') as infl:
            ls = infl.readlines()
    except IOError:
        print(("такого файла наверное нет.\n%s" % fl))
        return 0
    ro = float(ls[0])
    return ro


def prtk_copy_file(dir, dirin, mt, ro, im, dg, exist_list):
    fs = os.path.join(dirin, mt)
    fl = os.path.join(fs, 'RO_' + mt)
    ro_t = read_ro(fl)
    kf = ro / ro_t
    dg.write('Ro = {0}; Ro normal = {1}; Kff = {2}; \n'.format(ro, ro_t, kf))
    tt = glob.glob(fs + os.sep + '_*')
    nf = [os.path.split(ff)[-1] for ff in tt]
    prc = [ff.split('_')[1] for ff in nf]


    for i in im:
        ie = '{0:03d}'.format(i)
        for pp in prc:
            if f'_{pp}_' in exist_list.keys():
                if exist_list.get(f'_{pp}_')[0] == 1:
                    f_old = '_' + pp + '_' + mt
                    fsp = os.path.join(fs, f_old)
                    ls = prt[pp](fsp, kf)
                    f_new = '_' + pp + '_' + ie
                    fd = os.path.join(dir, f_new)
                    dg.write(' {0} => {1} \n'.format(f_old, f_new))
                    with open(fd, 'w') as ff:
                        ff.writelines(ls)
        pass

    pass


def par_path(initial_dir):
    for f in os.listdir(initial_dir):
        if f.endswith(".PAR") or f.endswith(".PAR"):
            path = f
    return path


## Функция для пересчета таблиц
#
def main(dp):
    """
    """
    k = 1

    dly = cord.read_layer(dp['lay'], nmfl='')
    idir_ = os.path.dirname(dp.get('rmp', ''))
    pdir = os.path.join(os.path.dirname(__file__), dir_file)
    tt = glob.glob(pdir + os.sep + '*')
    pmat = [os.path.split(ff)[-1] for ff in tt if os.path.isdir(ff)]

    ##    pmat = [ff.split('_')[-1].lower() for ff in pfil]
    ##    pmat = set(pmat)

    fllog = os.path.join(idir_, 'log_table_prtk.txt')

    dlog = open(fllog, 'w')
    print(fllog)

    par_dir = os.path.join(idir_, par_path(idir_))
    part_list = Project_reader.DataParcer(par_dir).par_decoder()
    exist_dict = {}
    for dicts in part_list:
        for key in dicts.keys():
            if dicts.get(key)[0] == 1:
                exist_dict.update({key: dicts.get(key)})
    print(exist_dict)

    for mat_, ro in list(dly.keys()):
        mt = mat_.upper()
        lmat = dly[(mat_, ro)]
        if mt in pmat:
            prtk_copy_file(idir_, pdir, mt, ro, lmat, dlog, exist_dict)

            sx = 'For {material} Density = {density} {lay}'.format(material=mat_, density=ro, lay=lmat)
            print(sx)
            dlog.write(sx + '\n')

    if True:
        pass

    dlog.close()


if __name__ == '__main__':

    file_name = os.path.join(os.path.dirname(__file__), 'defall.proj')
    ff = open(file_name, 'r')
    bd = yaml.load(ff)

    print('пересчитываем таблицы')
    main(bd)
    exit(0)

    sd = os.path.join(os.path.dirname(__file__), 'prtk_files')
    kk = 10.0

    nf = os.path.join(sd, '_ION_AIR')

    ls = ff_ion(nf, kk)

    try:
        with open(os.path.join(sd, 'ion'), 'w') as ff:
            ff.writelines(ls)
    except IOError:
        print(("такого файла наверное нет.\n%s" % ff))

    nf = os.path.join(sd, '_ATT_AIR')
    ls = ff_att(nf, kk)

    try:
        with open(os.path.join(sd, 'att'), 'w') as ff:
            ff.writelines(ls)
    except IOError:
        print(("такого файла наверное нет.\n%s" % ff))

    nf = os.path.join(sd, '_ROT_AIR')
    ls = ff_rot(nf, kk)

    try:
        with open(os.path.join(sd, 'rot'), 'w') as ff:
            ff.writelines(ls)
    except IOError:
        print(("такого файла наверное нет.\n%s" % ff))

    nf = os.path.join(sd, '_ELA_AIR')

    ls = ff_ela(nf, kk)

    try:
        with open(os.path.join(sd, 'ela'), 'w') as ff:
            ff.writelines(ls)
    except IOError:
        print(("такого файла наверное нет.\n%s" % ff))

    exit(0)
