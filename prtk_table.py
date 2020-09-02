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
import shutil
import numpy as np
from functools import reduce

Debug_ = False

if Debug_:
    try:
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib import cm
        from matplotlib.ticker import LinearLocator

        import matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

    ##    from mpl_toolkits.mplot3d.axes3d import Axes3D
    except:
        iPlot = False
    else:
        iPlot = True
        from matplotlib import rc

        font = {'family': 'Verdana',
                'weight': 'normal'}
        rc('font', **font)

import xxfun as xox
import phisconst as phis
import Project_reader_tables

import compoz_read as cord

## Словарь для хранения необходимых данных

parot_ = {}

parot_['.xer'] = {'name_out': 'FBB_E_'}
parot_['.xer']['data'] = ' {0:<12.4E}   {1:<12.4E}   {2:<12.4E}\n'
parot_['.xer']['head'] = """\
Сила торможения электронов в {material} ro = {density}
Число строк данных
 {nE}

Энергия(МэВ) Торм полн(МэВ/см) Торм в ионизированном воздухе(МэВ/см)""" + '\n'

parot_['.528'] = {'name_out': '_EXC_'}
parot_['.528']['data'] = ' {0:<12.5E}   {1:<12.5E}       {2:<12.5E}\n'
parot_['.528']['head'] = """\
Возбуждение электронов в {material}
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ)
1
ЧИСЛО УРОВНЕЙ ЭНЕРГИИ ЭЛЕКТРОНА
 1

НОМЕР УРОВНЯ ЭНЕРГИИ
 1
ЭНЕРГИЯ ВОЗБУЖДЕНИЯ(МэВ)
{Emin}
Число строк данных
 {nE}
Энергия(МэВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ) Потеря энергии(МэВ) """ + "\n"

parot_['.ann'] = {'name_out': '_ANN_'}
parot_['.ann']['data'] = ' {0:<12.5E}   {1:<12.5E}\n'
parot_['.ann']['head'] = """\
{material} АННИГИЛЯЦИЯ
ТАБЛИЦА ОБРАТНОГО ВРЕМЕНИ ПРОБЕГА(1/С)
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ ПОЗИТРОНА
 {nE}

Энергия(МэВ) ОБРАТНОЕ ВРЕМЯ ПРОБЕГА(1/С) """ + "\n"

parot_['.ive'] = {'name_out': '_KOM_'}
parot_['.ive']['data'] = ' {0:<12.5E}  {1:<12.4E}      '
parot_['.ive']['head'] = """\
{material} КОМПТОН ЭФФЕКТ
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ), ЭНЕРГИЙ ВЫЛЕТАЮЩЕГО КВАНТА(МЭВ)
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ КВАНТА
 {nE}
РАЗМЕРНОСТЬ ПО ВТОРОМУ АРГУМЕНТУ
 {nG}

ЭНЕРГИЯ(МэВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ) ЭНЕРГИЯ(МЭВ) КВАНТА - ФУНКЦИЯ РАВНОМЕРНО РАСПРЕДЕЛЕННОЙ НА [0,1] СЛУЧ ВЕЛИЧИНЫ""" + "\n"

parot_['.516'] = {'name_out': '_PAR_'}
parot_['.516']['data'] = ' {0:<12.5E}  {1:<12.4E}      '
parot_['.516']['head'] = """\
{material}  ОБРАЗОВАНИЕ ПАР
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ), ЭНЕРГИЙ ВЫЛЕТАЮЩЕГО ЭЛЕКТРОНА(МЭВ)
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ КВАНТА
 {nE}
РАЗМЕРНОСТЬ ПО ВТОРОМУ АРГУМЕНТУ
 {nG}

ЭНЕРГИЯ(МэВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ) ЭНЕРГИЯ(МЭВ) ЭЛЕКТРОНА - ФУНКЦИЯ РАВНОМЕРНО РАСПРЕДЕЛЕННОЙ НА [0,1] СЛУЧ ВЕЛИЧИНЫ""" + "\n"

parot_['.522'] = {'name_out': '_FOT_'}
parot_['.522']['data'] = ' {0:<12.4E}   {1:<12.4E}   {2:<12.4E}\n'
parot_['.522']['head'] = """\
{material} ФОТО ЭФФЕКТ
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ)
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ КВАНТА
 {nE}

ЭНЕРГИЯ(МЭВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ) Энергия связи(MeV)""" + "\n"

parot_['.527'] = {'name_out': '_BRM_'}
parot_['.527']['data'] = ' {0:<12.5E}  {1:<12.4E}      '
parot_['.527']['head'] = """\
{material} РАДИАЦИОННОЕ РАССЕЯНИЕ
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ), ЭНЕРГИЙ ВЫЛЕТАЮЩЕГО КВАНТА(МЭВ)
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ ЭЛЕКТРОНА
 {nE}
РАЗМЕРНОСТЬ ПО ВТОРОМУ АРГУМЕНТУ
 {nG}

ЭНЕРГИЯ(МэВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ) ЭНЕРГИЯ(МЭВ) КВАНТА - ФУНКЦИЯ РАВНОМЕРНО РАСПРЕДЕЛЕННОЙ НА [0,1] СЛУЧ ВЕЛИЧИНЫ""" + "\n"

parot_['.555'] = {'name_out': '_ION_'}
parot_['.555']['data'] = ' {0:<14.6E}     {1:<14.6E}      {2:<14.6E} '
parot_['.555']['head'] = """\
{material} ИОНИЗАЦИЯ
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ), ЭНЕРГИЙ ВЫЛЕТАЮЩЕГО ЭЛЕКТРОНА(МЭВ)
1
ЧИСЛО УРОВНЕЙ ЭНЕРГИИ ЭЛЕКТРОНА
1
РАЗМЕРНОСТЬ ПО ВТОРОМУ АРГУМЕНТУ
 {nG}

НОМЕР УРОВНЯ ЭНЕРГИИ
1
ПЕРЕДАВАЕМАЯ ЭНЕРГИЯ
{Emin}
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ ЭЛЕКТРОНА
 {nE}
ЭНЕРГИЯ(МэВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ)  СРЕДНЯЯ ЭНЕРГИЯ(МэВ)  ЭНЕРГИЯ(МэВ) ЭЛЕКТРОНА - ФУНКЦИЯ РАВНОМЕРНО РАСПРЕДЕЛЕННОЙ НА [0,1] СЛУЧ ВЕЛИЧИНЫ""" + "\n"

parot_['.526'] = {'name_out': '_ELA_'}
parot_['.526']['data'] = ' {0:<12.5E}  {1:<12.4E}      '
parot_['.526']['head'] = """\
{material} УПРУГОЕ РАССЕЯНИЕ
ТАБЛИЦА ПОЛНЫХ СЕЧЕНИЙ(1/СМ), УГОЛ ВЫЛЕТПЮЩНГО ЭЛЕКТРОНА
ЧИСЛО ЗНАЧЕНИЙ ЭНЕРГИИ ЭЛЕКТРОНА
 {nE}
РАЗМЕРНОСТЬ ПО ВТОРОМУ АРГУМЕНТУ
 {nG}
ПЕРЕДАВАЕМАЯ ДОЛЯ ЭНЕРГИИ ЭЛЕКТРОНА
{Epp}

ЭНЕРГИЯ(МэВ) ПОЛНОЕ СЕЧЕНИЕ(1/СМ) ЭНЕРГИЯ(МЭВ) КВАНТА - ФУНКЦИЯ РАВНОМЕРНО РАСПРЕДЕЛЕННОЙ НА [0,1] СЛУЧ ВЕЛИЧИНЫ""" + "\n"


## Функция для считывания материалов, для которых
# необходимо пересчитать таблицы
#
def par_path(initial_dir):
    for f in os.listdir(initial_dir):
        if f.endswith(".PAR") or f.endswith(".PAR"):
            path = f
    return path


def lay_path(initial_dir):
    for f in os.listdir(initial_dir):
        if f.endswith(".LAY") or f.endswith(".LAY"):
            path = f
    return path


def copy_file(dir, nf, im):
    if len(im) == 1:
        return
    fs = os.path.join(dir, nf + '{0:03d}'.format(im[0]))

    for i in im[1:]:
        fd = os.path.join(dir, nf + '{0:03d}'.format(i))
        shutil.copyfile(fs, fd)
        pass

    pass


def prtk_copy_file(dir, nf, im):
    if len(im) == 1:
        return
    fs = os.path.join(dir, nf + '{0:03d}'.format(im[0]))

    for i in im[1:]:
        fd = os.path.join(dir, nf + '{0:03d}'.format(i))
        shutil.copyfile(fs, fd)
        pass

    pass


def get_list_material(mat_fl_):
    tt_ = []
    with open(mat_fl_, 'rt') as f_In_:
        for k, line_ in enumerate(f_In_):
            tt_.append(line_.split()[0])
    return tt_


## Функция для пересчета таблиц
#
def main(dp):
    dly = cord.read_layer(dp['lay'], nmfl='')
    print(len(dly))
    nG_ = dp.get('nG', 201)
    print('Ng = {0}'.format(nG_))
    gg_ = np.linspace(0.0, 1.0, nG_)
    idir_ = os.path.dirname(dp.get('rmp', ''))
    fllog = os.path.join(idir_, 'log_table.txt')
    dlog = open(fllog, 'w')
    print(fllog)

    par_dir = os.path.join(idir_, par_path(idir_))
    part_list = Project_reader_tables.DataParcer(par_dir).par_decoder()
    move, io_brake, layers_numbers = Project_reader_tables.DataParcer(par_dir.replace('.PAR', '.PL')).pl_decoder()
    cond_six = False
    lay_dir = os.path.join(idir_, lay_path(idir_))
    _, co = Project_reader_tables.DataParcer(lay_dir).lay_decoder()
    if any([i == 6 for i in co]):
        cond_six = True

    io_brake_dict = {}
    move_dict = {}
    for i in range(layers_numbers.shape[0]):
        io_brake_dict.update({layers_numbers[i]: io_brake[:, i]})
        move_dict.update({layers_numbers[i]: move[:, i]})

    print(f'io br  {io_brake_dict}')
    print(f'move  {move_dict}')

    ##    mat_fl_ = dp['mf']
    ##    nm_comp_ = get_list_material(mat_fl_)

    for mat_, Ro_ in dly.keys():
        mt_ = 'mat-' + mat_
        imat = dly[(mat_, Ro_)][0]
        dir_mat_ = os.path.join(dp.get('tab', ''), mt_)

        dir_mat_el_ = os.path.join(dir_mat_, 'electron')
        dir_mat_ph_ = os.path.join(dir_mat_, 'photon')

        cs_el_, heap_el_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl.23p'))
        xx_ = heap_el_[7].split()
        Am_ = float(xx_[1])
        ##        Ro_ = float(xx_[2])
        log_E_ = np.array(cs_el_[:, 0])
        Eev_ = np.power(10, log_E_)
        E_ = Eev_ * 10 ** (-6)
        nE_ = len(E_)
        cs_el_ = Ro_ * np.power(10, cs_el_[:, 1:])
        sx = 'In {material} Density = {density}'.format(material=mat_, density=Ro_)
        print(sx)
        dlog.write(sx + '\n')

        # ---------------------------------------------------------------------------------
        key_ = '.xer'
        xer_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl' + key_))
        xer_ = np.array(xer_)
        xer_ = Ro_ * np.power(10, xer_[:, 1:]) * 10 ** (-6)
        ttl_ = np.sum(xer_, axis=1)
        ttl_st_ = ttl_ - xer_[:, -1]
        ff_ = parot_[key_]['name_out']

        if mat_ == 'air' or mat_ == 'vozduch':
            # pattern_file_path = r'C:\Users\Nick\Dropbox\work_cloud\xtb\mat_files\FBB_example'
            pattern_file_path = os.path.join(os.path.abspath(__file__), r'mat_files\FBB_example')
            pattern_file_path = os.path.normpath(pattern_file_path)

            data, ro_pat = example_fbb_file_reader(pattern_file_path)
            data = data * Ro_ / ro_pat

            vz_ = zip(E_, ttl_, data)

        else:
            vz_ = zip(E_, ttl_, ttl_st_)

        # данные по шаманству fbb тут нужная строка в vz_[2]
        if np.any(io_brake_dict.get(int(imat))[:] == 1):
            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_, density=Ro_))
                for v_ in vz_:
                    out_.write(parot_[key_]['data'].format(v_[0], v_[1], v_[2]))
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

        exist_dict = {}
        for i, part_dict in enumerate(part_list):
            for key in part_dict.keys():
                part_dict_vals = part_dict.values()
                part_number = key

            if move_dict.get(imat)[part_number] == 1:
                for components in part_dict_vals:
                    for item in components.items():
                        if item[1][0] == 1:
                            exist_dict.update({item[0]: item[1][0]})
        print(exist_dict)
        # ---------------------------------------------------------------------------------
        key_ = '.ann'
        xt_ = cs_el_[:, -1]
        xg_ = (phis.E0 + Eev_) / phis.E0
        sl_c = 29979245800.0  # cm/s
        xv_ = sl_c * np.sqrt(1.0 - (1. / xg_) ** 2)
        vz_ = zip(E_, xt_ * xv_)
        ff_ = parot_[key_]['name_out']
        if ff_ in exist_dict.keys():

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_))
                for v_ in vz_:
                    out_.write(parot_[key_]['data'].format(v_[0], v_[1]))
            copy_file(idir_, ff_, dly[(mat_, Ro_)])
        # ---------------------------------------------------------------------------------
        key_ = '.528'
        xer_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl' + key_))
        xer_ = np.array(xer_)
        ##        xer_ = Ro_ * np.power(10, xer_[:, 1:]) * 10**(-6)
        ##        ttl_ = np.sum(xer_, axis=1)
        ##        ttl_st_ = ttl_ - xer_[:,-1]
        vz_ = zip(E_, cs_el_[:, 2], np.power(10, xer_[:, 1]) * 10 ** (-6))
        ff_ = parot_[key_]['name_out']  # _EXC_
        if ff_ in exist_dict.keys() or cond_six is True:

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, Emin=E_[0], nE=nE_))
                for v_ in vz_:
                    out_.write(parot_[key_]['data'].format(v_[0], v_[1], v_[2]))
            copy_file(idir_, ff_, dly[(mat_, Ro_)])
        # ---------------------------------------------------------------------------------
        key_ = '.526'
        rr_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl' + key_))
        rr_ = np.transpose(rr_)
        gamma_ = np.linspace(float(heap_[7].split()[0]), 0, int(heap_[7].split()[1]) - 1)
        p_rr_ = -1.0 * np.ones((nE_, nG_))
        gg_lg = np.log10(gg_[1:])
        ##        gamma_lg = np.log10(gamma_[1:])
        for k_ in range(nE_):
            p_rr_[k_, 1:] = np.interp(gg_lg, gamma_, rr_[k_, 1:])
        p_rr_[:, 1:] = np.power(10, p_rr_[:, 1:]) - 1
        ##        for k_ in xrange(nE_):
        ##            p_rr_[k_, :] = np.interp(gg_, gamma_, rr_[k_, :])
        ##        p_rr_[:, 1:] = np.power(10,p_rr_[:, 1:])-1
        ##        p_rr_ = np.power(10, p_rr_) * 10 **(-6)
        vz_ = zip(E_, cs_el_[:, 0])
        ff_ = parot_[key_]['name_out']  # _ELA_
        if ff_ in exist_dict.keys() or cond_six is True:

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(
                    parot_[key_]['head'].format(material=mat_, nE=nE_, Epp=2.0 * phis.ms_el_gr / Am_, nG=nG_))
                for k_, v_ in enumerate(vz_):
                    ss_ = parot_[key_]['data'].format(v_[0], v_[1])
                    vv_ = p_rr_[k_, :]
                    ##                vv_= np.arccos(vv_[::-1])
                    vv_ = vv_[::-1]
                    tt = vv_[-2] + (vv_[-2] - vv_[-3])  # /(gg_[-2]-gg_[-3])
                    vv_[-1] = max(tt, -1.)
                    vv_[0] = 1.0
                    vv_ = np.arccos(vv_)

                    ##                vv_[0] = 0.0
                    mm_ = ['{0:12.5E} '.format(c_) for c_ in vv_]
                    out_.write(ss_ + reduce(lambda a, b: a + b, mm_) + '\n')
            ##
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

        # ---------------------------------------------------------------------------------
        key_ = '.527'
        rr_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl' + key_))
        rr_ = np.transpose(rr_)
        gamma_ = np.linspace(0., 1., rr_.shape[1])
        p_rr_ = np.zeros((nE_, nG_))
        for k_ in range(nE_):
            p_rr_[k_, :] = np.interp(gg_, gamma_, rr_[k_, :])
        p_rr_ = np.power(10, p_rr_) * 10 ** (-6)
        vz_ = zip(E_, cs_el_[:, 1])
        ff_ = parot_[key_]['name_out']  # _BRM_
        if ff_ in exist_dict.keys():

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_, nG=nG_))
                for k_, v_ in enumerate(vz_):
                    ss_ = parot_[key_]['data'].format(v_[0], v_[1])
                    vv_ = p_rr_[k_, :]
                    vv_ = vv_[::-1]
                    vv_[0] = 0.0
                    mm_ = ['{0:12.5E}'.format(c_) for c_ in vv_]
                    out_.write(ss_ + reduce(lambda a, b: a + b, mm_) + '\n')
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

        # ---------------------------------------------------------------------------------

        cs_ph_, heap_ph_ = xox.read_kiam_file(os.path.join(dir_mat_ph_, 'xtbl.23'))
        cs_ph_ = Ro_ * np.power(10, cs_ph_[:, 1:])
        # ---------------------------------------------------------------------------------

        key_ = '.522'
        eb_ph_, heap__ = xox.read_kiam_file(os.path.join(dir_mat_ph_, 'xtbl.eb'))
        eb_ph_ = eb_ph_[:, -1] * 10 ** (-6)
        vz_ = zip(E_, cs_ph_[:, -1], eb_ph_)
        ff_ = parot_[key_]['name_out']  # _FOT_
        if ff_ in exist_dict.keys():

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_, bE=eb_ph_[-1]))
                for v_ in vz_:
                    out_.write(parot_[key_]['data'].format(v_[0], v_[1], v_[2]))
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

        # ---------------------------------------------------------------------------------

        key_ = '.ive'
        ive_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_ph_, 'xtbl.ive'))
        ive_ = np.transpose(ive_)
        gamma_ = np.linspace(0., 1., ive_.shape[1])
        p_ive_ = np.zeros((nE_, nG_))
        for k_ in range(nE_):
            p_ive_[k_, :] = np.interp(gg_, gamma_, ive_[k_, :]) * 10 ** (-6)
        vz_ = zip(E_, cs_ph_[:, 2])
        ff_ = parot_[key_]['name_out']  # _KOM_
        if ff_ in exist_dict.keys():

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_, nG=nG_))
                for k_, v_ in enumerate(vz_):
                    ss_ = parot_[key_]['data'].format(v_[0], v_[1])
                    mm_ = ['{0:12.5E}'.format(c_) for c_ in p_ive_[k_, :]]
                    out_.write(ss_ + reduce(lambda a, b: a + b, mm_) + '\n')
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

        # ---------------------------------------------------------------------------------

        key_ = '.516'
        rr_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_ph_, 'xtbl' + key_))
        rr_ = np.transpose(rr_)
        gamma_ = np.linspace(float(heap_[7].split()[0]), 0, int(heap_[7].split()[1]) - 1)
        p_rr_ = np.zeros((nE_, nG_))
        gl_ = np.log10(gg_[1:])
        for k_ in range(nE_):
            p_rr_[k_, 1:] = np.interp(gl_, gamma_, rr_[k_, 1:])
        p_rr_[:, 1:] = np.power(10, p_rr_[:, 1:]) * 10 ** (-6)
        i_rr_ = (p_rr_ < 1.E-16)
        E2_ = 2 * phis.E0 / 10 ** 6
        nE_ = sum(E_ > E2_) + 1
        p_rr_[i_rr_] = 0.0
        vz_ = zip(E_, cs_ph_[:, 3])
        ff_ = parot_[key_]['name_out']  # _PAR_
        if ff_ in exist_dict.keys():

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_, nG=nG_))
                ##            ss_ = parot_[key_]['data'].format(1.0, 0.0)
                ss_ = parot_[key_]['data'].format(E2_, 0.0)
                vt_ = 0.0 * np.ones(nG_)
                mm_ = ['{0:12.5E}'.format(c_) for c_ in vt_]
                out_.write(ss_ + reduce(lambda a, b: a + b, mm_) + '\n')

                for k_, v_ in enumerate(vz_):
                    if E_[k_] >= E2_:
                        vv_ = p_rr_[k_, :]
                        dd_ = v_[0] - E2_ - vv_[-1]
                        dlog.write('E = {0}: Delta ={1}\n'.format(v_[0], dd_) + '\n')
                        if dd_ < 0.:
                            dlog.write('Vend = {0} '.format(v_[-1]) + '\n')

                            vv_[-1] = v_[0] - E2_
                            dlog.write('Change on Vend = {0}\n'.format(v_[-1]) + '\n')

                        ss_ = parot_[key_]['data'].format(v_[0], v_[1])
                        mm_ = ['{0:12.5E}'.format(c_) for c_ in p_rr_[k_, :]]
                        out_.write(ss_ + reduce(lambda a, b: a + b, mm_) + '\n')
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

        # ---------------------------------------------------------------------------------

        key_ = '.555'
        eb_el_, heap__ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl.eb'))
        eb_el_ = eb_el_[:, -1] * 10 ** (-6)

        ra_, ha_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl' + '.awe'))
        p_ra_ = np.power(10, ra_[:, 1]) * 10 ** (-6)
        rr_, heap_ = xox.read_kiam_file(os.path.join(dir_mat_el_, 'xtbl' + key_))
        nE_ = rr_.shape[1]
        rr_ = np.transpose(rr_)
        rrv_ = np.power(10, rr_)
        gamma_ = np.logspace(float(heap_[7].split()[0]), 0, int(heap_[7].split()[1]) - 1)
        p_rr_ = np.zeros((nE_, nG_))
        gl_ = np.log10(gg_[1:])
        for k_ in range(nE_):
            # p_rr_[k_, 1:] = np.interp(gl_, gamma_, rr_[k_, 1:])
            p_rr_[k_, 1:] = np.interp(gg_[1:], gamma_, rrv_[k_, 1:])
            p_rr_[k_, 0] = rrv_[k_, 0]
        ##        p_rr_ = np.power(10, p_rr_) * 10 **(-6)
        xeb_ = (E_ - eb_el_) / 2. * 10 ** (-6)
        p_rr_[:, -1] = xeb_
        vz_ = zip(E_, cs_el_[:, 3])
        ff_ = parot_[key_]['name_out']  # _ION_
        if ff_ in exist_dict.keys():

            with open(os.path.join(idir_, ff_ + '{0:03d}'.format(imat)), 'w') as out_:
                out_.write(parot_[key_]['head'].format(material=mat_, nE=nE_, Emin=E_[0], nG=nG_))
                for k_, v_ in enumerate(vz_):
                    ss_ = parot_[key_]['data'].format(v_[0], v_[1], p_ra_[k_])
                    vv_ = p_rr_[k_, ::-1]
                    mm_ = ['{0:12.5E}'.format(c_) for c_ in vv_]
                    out_.write(ss_ + reduce(lambda a, b: a + b, mm_) + '\n')
            copy_file(idir_, ff_, dly[(mat_, Ro_)])

    if True:
        pass

    dlog.close()
    print(u'Модуль пересчета распределений для РЭМП закончил свою работу')


def create_parser():
    parser = argparse.ArgumentParser(
        prog='prtk_table.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@',
        description=textwrap.dedent(u'''\
     Программа для пересчета таблиц в формат программного комплекса РЭМП
     ---------------------------------------------------------------------'''),
        epilog=phis.epic,
        add_help=False)

    parent_group = parser.add_argument_group(title=u'Параметры')
    parent_group.add_argument('--help', '-h', action='help', help=u'Справка')

    parent_group.add_argument('-f', '--file', type=str, action='store',
                              default='materials',
                              help=u'Наименование исходного файла со списком композитов')

    parent_group.add_argument("-N", "--Nxi", action='store', type=int,
                              default=201,
                              help=u'Количество точек в выходных таблицах')

    return parser


def example_fbb_file_reader(path):
    data = np.loadtxt(path, skiprows=5, dtype=float)

    with open(path, 'r') as file:
        line = file.readline()

    ro = float(line.strip().split('=')[-1])

    return data[:, 2], ro


if __name__ == '__main__':
    pattern_file_path = r'C:\Users\Nick\Dropbox\work_cloud\xtb\mat_files\FBB_example'
    a, b = example_fbb_file_reader(pattern_file_path)
    print(a, b)
# import yaml
#
# nG_ = 21
#
# file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
# ff = open(file_name, 'r')
# bd = yaml.load(ff)
#
# print(u'пересчитываем таблицы')
# main(bd)
# exit(0)
#
# try:
#     import argparse
#     import textwrap
#     import yaml
#
#     parser = create_parser()
#     args_ = vars(parser.parse_args())
#     nG_ = args_['Nxi']
#     name_file_ = args_['file']
#     #        print(args_)
#     file_name = os.path.join(os.path.dirname(__file__), 'config.yml')
#     ff = open(file_name, 'r')
#     bd = yaml.load(ff)
#
#     print(u'пересчитываем таблицы')
#     main(bd)
# except ImportError:
#     print(u"Старый Питон")
#     main(bd)
#     pass
# else:
#     pass
# finally:
#     pass
