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

import numpy as np

import compoz_read as cord
import Project_reader_tables


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


def ff_elt(fl, kf):
    with open(fl, 'r', encoding='utf-8') as infl:
        ls = infl.readlines()

    description = ls[:10]

    fs = description

    array = []
    for ll in ls[10:]:
        array.append(ll.strip().split())

    array = np.array(array, dtype=float)

    for i in range(array.shape[0]):
        string = '{:6.5E}  {:6.5E}  '.format(array[i, 0], array[i, 1] * kf)
        fu = ''
        for j in range(2, array.shape[1]):
            fu += '{:6.5E}'.format(array[i, j]) + '  '

        fs.append(string + fu + '\n')

    return fs


prt = {'ELA': ff_ela, 'EXC': ff_exc, 'ION': ff_ion,
       'ROT': ff_rot, 'ATT': ff_att, 'REC': ff_rec,
       'ELT': ff_elt}


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

    path_dict = Project_reader_tables.check_folder(dir)
    lay_dir = os.path.join(dir, path_dict['LAY'])
    layers_data, conductivity = Project_reader_tables.DataParcer(lay_dir).lay_decoder()

    lay_conductivity_dict = {}
    for i in range(len(layers_data)):
        lay_conductivity_dict.update({int(layers_data[i][0]): conductivity[i]})

    for i in im:
        ie = '{0:03d}'.format(i)
        for pp in prc:
            if f'_{pp}_' in exist_list.keys():
                if int(exist_list.get(f'_{pp}_')) != 0:
                    write_prtk_files(pp, mt, fs, kf, ie, dg, dir)

            # elif lay_conductivity_dict[i] == 6:
            #     if pp == 'ELA':
            #         write_prtk_files('ELT', mt, fs, kf, ie, dg, dir)
            #     else:
            #         write_prtk_files(pp, mt, fs, kf, ie, dg, dir)


def write_prtk_files(pp, mt, fs, kf, ie, dg, dir):
    f_old = '_' + pp + '_' + mt
    fsp = os.path.join(fs, f_old)
    ls = prt[pp](fsp, kf)
    f_new = '_' + pp + '_' + ie
    fd = os.path.join(dir, f_new)
    dg.write(' {0} => {1} \n'.format(f_old, f_new))
    with open(fd, 'w') as ff:
        ff.writelines(ls)




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

    path_dict = Project_reader_tables.check_folder(idir_)

    par_dir = os.path.join(os.path.join(idir_, path_dict['PAR']))
    pl_dir = os.path.join(idir_, path_dict['PL'])

    part_list, part_types = Project_reader_tables.DataParcer(par_dir).par_decoder()
    move, io_brake, layers_numbers = Project_reader_tables.DataParcer(pl_dir).pl_decoder()

    move_dict = {}
    for i in range(layers_numbers.shape[0]):
        move_dict.update({layers_numbers[i]: move[:, i]})

    # print(exist_dict)

    for mat_, ro in list(dly.keys()):
        mt = mat_.upper()
        lmat = dly[(mat_, ro)]

        exist_dict = {}
        for i, part_dict in enumerate(part_list):
            for key in part_dict.keys():
                part_dict_vals = part_dict.values()
                part_number = key

            if move_dict.get(lmat[0])[part_number] == 1:
                for components in part_dict_vals:
                    for item in components.items():
                        if item[1][0] == 1:
                            exist_dict.update({item[0]: item[1][0]})
                # print(exist_dict)

        if mt in pmat:
            prtk_copy_file(idir_, pdir, mt, ro, lmat, dlog, exist_dict)

            sx = 'For {material} Density = {density} {lay}'.format(material=mat_, density=ro, lay=lmat)
            print(sx)
            dlog.write(sx + '\n')

    if True:
        pass

    dlog.close()


if __name__ == '__main__':

    import pickle

    with open(r'C:\Work\Test_projects\wpala\dp', 'rb') as f:
        dp = pickle.load(f)

    main(dp)
