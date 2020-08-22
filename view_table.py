#!/usr/bin/env python
# -*- coding: utf-8 -*-


## @package show_table
# Модуль для графического представления распределений
# при взаимодействии электрона и фотонов с веществом
#-------------------------------------------------------------------------------

version = '0.5.2'

import os
# import argparse

import numpy as np

import xxfun as xox
import phisconst as phis
import xxplot as xxp


from  sys import version_info

v=version_info[0]
if v==3:
    from tkinter import *                          # get widget classes
    from tkinter.filedialog import askopenfilename
else:
    from tkinter import *                          # get widget classes

from tkinter.filedialog import askopenfilename


ftypes =  [('All','.*'), ('Cross-Section','.23'),
        ('Elastic', '.526'),('Brems', '.527'),('Exit', '.528'),('Ionization', '.555'),
        ('Stop Power', '.stp'),('Average Energy', '.awe'),
        ('Binding Energy','.eb'), ('Para Produced', '.516'), ('Stopping Power','.xer'),
        ('Compton','.iv'),('Coherent','.cv')]

inter_e = ['23','526','527','528','555','stp','xer','awe','eb']
inter_e = ['23','.516','527','.528','.555','.stp','.xer','.awe','.eb']
xlor='rgbcmyk'

iSave = False
Title_ = False
iEnglish_ = False

def xsave(f):
    def tmp(*args, **kwargs):
        if iSave:
            res = f(*args, **kwargs)    #(args[0],args[1],args[2])
            return res
        return 0
    return tmp

@xsave
def gsave(name_):
    xxp.xsave_fig(name_)

def plot_file(dp):
    """
    """
    matFile_ = dp['mtf']
    fig_ =  dp['fig']
    Ro = dp['ro']
    L = phis.E0
    K = phis.Kph
    if iEnglish_:
        xlE_ = '$E,eV$'
    else:
        xlE_ = '$\varepsilon,эВ$'

##    print(xlE_)
    xlG_ =r'$\xi$'
    xproc_={}
    xproc_['.23'] = {'title':'Cross Section','ptkl':'ph','xlabel':xlE_,'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.23p'] = {'title':'Cross Section','ptkl':'pz','xlabel':xlE_,'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.eb'] = {'title':'Binding Energy','ptkl':'el','xlabel':xlE_,'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.iv'] = {'title':'Комптоновское рассеяние','ptkl':'ph','xlabel': xlG_, 'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.cv'] = {'title':'Когерентное рассеяние','ptkl':'ph','xlabel':xlG_,'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.516'] = {'title':'Рождение электрон-позитронных пар','ptkl':'ph','xlabel':xlG_,'ylabel':r'$\varepsilon_{e^+}, эВ$'}
    xproc_['.526'] = {'title':'Упругое рассеяние','ptkl':'el','xlabel':xlG_,'ylabel':r'$log_{10}(1+cos(\theta_{e^-}))$'}
    if iEnglish_:
        xproc_['.527'] = {'title':'Тормозное излучение','ptkl':'el','xlabel':xlG_,'ylabel':r'$E_{\gamma}, eV$'}
    else:
        xproc_['.527'] = {'title':'Тормозное излучение','ptkl':'el','xlabel':xlG_,'ylabel':r'$\varepsilon_{\gamma}, эВ$'}
    xproc_['.528'] = {'title':'Excitation','ptkl':'el','xlabel':xlE_,'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.555'] = {'title':'Electroionization','ptkl':'el','xlabel':xlG_,'ylabel':r'$\varepsilon_{e^-}, эВ$'}
    xproc_['.stp'] = {'title':'Stop Power','ptkl':'el','xlabel':xlE_,'ylabel':'$cos(\theta_{\gamma})$'}
    xproc_['.awe'] = {'title':'Awerage Energy','ptkl':'el','xlabel':xlE_,'ylabel':'$cos(\theta_{\gamma})$'}
    xclor='rgbcmyk'
    fext_=os.path.splitext(matFile_)[-1]
    sd_ = os.path.normpath(matFile_).split('\\')
    material_ = sd_[-3].split('-')[1]
    particle_ = sd_[-2]
    if particle_ == 'electron':
        ptkl_ = 'el'
    elif particle_ == 'photon':
        ptkl_ = 'ph'
    ##        Считываются данные из файла
    rr_, hp=xox.read_kiam_file(matFile_)
    tt_ = hp[4].split()
    ee_ = np.logspace(float(tt_[0]), float(tt_[1]), int(tt_[2]))
    ne_ = len(ee_)
    ixe = range(1,ne_,(ne_//40+1))
##    lie_ = [1:ne_:(ne_//20+1)]
    opis_ = {}
    opis_['.23'] = {'ylabel':r'$\Sigma, \frac{см^2}{г}$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    opis_['.23p'] = opis_['.23'].copy()
    opis_['.awe'] = {'legenda':('потеря энергии при ионизации',
    'потеря энергии при возбуждении', 'потеря энергии при тормозном'),
     'ylabel':r'$\widehat{\varepsilon}, эВ$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    opis_['.xer'] = {'legenda':('Столкновительная тормозная способность',
    'Радиационная тормозная способность ', ),
     'ylabel':r'$\varkappa, эВ\cdot{\frac{см^2}{г}}$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper right'}
    opis_['.eb'] = {'legenda':('Энергия связи',),
     'ylabel':r'$\varepsilon_{b}, эВ$', 'bxlog': True,
     'bylog':False, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    if ptkl_ in ['ph']:
        opis_['.eb']['xlabel'] = r'$\varepsilon_{\gamma}, эВ$'

    opis_['.stp'] = {'legenda':('Тормозной путь',),
     'ylabel':r'$L, \frac{г}{см^2}$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    opis_['.528'] = {'legenda':('Средняя потеря энергии при возбуждении атома',),
     'ylabel':r'$\widehat{\varepsilon_{e^-}}, эВ$', 'bxlog': True,
     'bylog':False, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    opis_['.555'] = {'legenda':('Средняя энергия вторичного электрона',),
     'ylabel':r'$\widehat{\varepsilon_{e^-}}, эВ$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    opis_['.527'] = {'legenda':('Средняя энергия тормозного фотона',),
     'ylabel':r'$\widehat{\varepsilon_{\gamma}}, эВ$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    opis_['.526'] = {'legenda':('Средний косинус',),
     'ylabel':r'$\widehat{cos(\theta_{e^-})}$', 'bxlog': True,
     'bylog':False, 'xlabel':r'$\varepsilon_{e^-}, эВ$', 'place':'upper left'}
    if iEnglish_:
       opis_['.iv'] = {'legenda':('Средний косинус',),
     'ylabel':r'$\widehat{cos(\theta)}$', 'bxlog': True,
     'bylog':False, 'xlabel':r'$E_{\gamma}, eV$', 'place':'upper left'}
    else:
       opis_['.iv'] = {'legenda':('Средний косинус',),
     'ylabel':r'$\widehat{cos(\theta)}$', 'bxlog': True,
     'bylog':False, 'xlabel':r'$\varepsilon_{\gamma}, эВ$', 'place':'upper left'}
    opis_['.cv'] = {'legenda':('Средний косинус',),
     'ylabel':r'$\widehat{cos(\theta)}$', 'bxlog': True,
     'bylog':False, 'xlabel':r'$\varepsilon_{\gamma}, эВ$', 'place':'upper left'}
    opis_['.516'] = {'legenda':('Средняя энергия позитрона',),
     'ylabel':r'$\widehat{\varepsilon_{e^+}}$', 'bxlog': True,
     'bylog':True, 'xlabel':r'$\varepsilon_{\gamma}, эВ$', 'place':'upper left'}
    if Title_:
        opis_[fext_]['title'] = 'Материал {0} '.format(material_[4:])
    else:
        opis_[fext_]['title'] =''
    gr_name_ = material_ + '_' + ptkl_ + '_' + fext_[1:] + '_'
    if fext_ in ['.23','.23p', '.eb','.stp','.awe', '.xer', '.528']:
        if fext_ != '.eb':
            rr_ = np.power(10,rr_)
        else:
            rr_[:, 0] = np.power(10,rr_[:,0])

        xx_ = rr_[:, 0]
        yy_ = rr_[:, 1:]
        if fext_ == '.xer':
            yy_ [:, 0] = rr_[:, 1] + rr_[:, 2]
            yy_ [:, 1] =  rr_[:, 3]
            yy_ = yy_ [:, 0:2]


        if fext_ in ['.awe', '.xer', '.eb', '.stp', '.528']:
            fig_ = 1
            xxp.xgraf_plot(xx_, yy_, gr_name_, opis_[fext_] )
            gsave(gr_name_)
            if fext_ in ['.stp']:
                fig_ += 1
                opis_[fext_]['ylabel'] = r'$L, см$'
                opis_[fext_]['xlabel'] = r'$\varepsilon, эВ$'

##                opis_[fext_]['bxlog'] = False
##                Ro = 2.7
                xxp.xgraf_plot(xx_, yy_/Ro, gr_name_ + str(Ro), opis_[fext_] )
                pass

        elif fext_ in ['.23', '.23p']:
            ## Получаем плотность композита
##            Ro = float(hp[7].split()[2])

            if ptkl_ == 'el' :
                ful_ = np.sum(yy_, axis=1)
                nr, nc = yy_.shape
                ye_ = np.zeros((nr, nc+1))
##                print(yy_.shape)
##                print(ye_.shape)
##                print(ful_.shape)
                xy_ =  Ro * ful_
                ye_[:, 1:] = yy_[:,:]
                ye_[:, 0] = ful_
                yy_ = np.copy(ye_)
                xy_ = 1. / xy_

##                opis_[fext_]['legenda'] = (u'Полное сечение', u'Упругое рассеяние', u'Тормозное излучение ',
##                u'Возбуждение атома', u'Электроионизация', u'Аннигиляция', )
                opis_[fext_]['legenda'] = ('Полное сечение', 'Упругое рассеяние', 'Тормозное излучение ',
                'Возбуждение атома', 'Электроионизация' )
                opis_[fext_]['xlabel'] = r'$\varepsilon_{e^-}, эВ$'
            elif ptkl_ == 'ph':
                 xy_ =  Ro * yy_[:, 0]
                 xy_ = 1. / xy_
                 opis_[fext_]['xlabel'] = r'$\varepsilon_{\gamma}, эВ$'
                 if np.max(xx_) < 2* phis.E0:
                     opis_[fext_]['legenda'] = ('Полное сечение',
                     'Когерентное рассеяние', 'Комптоновское рассеяние', 'Фотоионизация атома')
                     yy_ = np.delete(yy_,3,1)
                 else:
                     opis_[fext_]['legenda'] = ('Полное сечение',
                     'Когерентное рассеяние', 'Комптоновское рассеяние',
                     'Рождение электрон-позитронных пар', 'Фотоионизация атома')


            fig_ += 1
            opis_['len'] = opis_['.23'].copy()
            opis_['len']['ylabel'] = r'$см$'
            opis_['len']['legenda'] = ('Длина свободного пробега',)
            opis_['len']['title'] += r'$ \rho = $' + str(Ro)
            xxp.xgraf_plot(xx_, xy_, gr_name_ + str(Ro) + '_length', opis_['len'] )
            gsave(gr_name_ + '_lenth')

            fig_ += 1
            ip_ = yy_<10**(-15)
            yy_[ip_] = 0.
            xxp.xplot_cs(xx_, yy_, gr_name_, opis_[fext_])
            gsave(gr_name_)
##            opis_[fext_]['ylabel'] = r'$см^{-1}$'
            opis_[fext_]['ylabel'] = r'$\mu^{-1}, см$'
            xxp.xplot_cs(xx_, 1.0/(yy_*Ro), gr_name_ + str(Ro), opis_[fext_])


    else:
        nR_,nC_=rr_.shape
        if fext_ in ['.iv','.cv']:
            gg_ = np.linspace(0.,1.,nR_)
            yy_ = rr_
            cav_ = np.trapz(yy_, gg_, axis=0)

            fig_ += 1

            xxp.xtable_plot(ee_[ixe], gg_, yy_[:,ixe], gr_name_ + "_table", bxlog = False, bylog = False,
                            ylabel = r'$cos(\theta)$', xlabel = r'$\xi$' )
            gsave(gr_name_ + "_table")

            nn_ = nR_
            Qmax = phis.Kph/phis.E0*ee_[-1]*np.power(2.,0.5)
            q_= np.linspace(0.0,Qmax,nn_)
            x_ = 1. - np.power((phis.E0 * q_/phis.Kph/ee_[-1]), 2)
            tt_ = x_[::-1]
            tt_[0] = -1.
            tt_[-1] = 1.
            hh_ = np.diff(tt_)

##            tt_ = np.linspace(-1, 1, nn_)
##            hh_ = 2. / (nn_ - 1)
##            tt_ = tt_[:-1]
            xt_ = tt_[:-1] + hh_ /2.

            Df_ = np.zeros((len(ee_), nn_ - 1))
            dfm_ = np.zeros((len(ee_), nn_ - 1))
            dem_ = np.zeros(( nn_, len(ee_) ))
            eav = np.zeros_like(cav_)
            for i, e_ in enumerate(ee_):
                dd_ = np.interp(tt_, yy_[:,i], gg_)
                df_ = np.diff(dd_) / hh_
                sm_ = np.trapz(df_, xt_)
                df_ /= sm_
                if fext_ in ['.iv']:
                    Eph_ = e_ / (1. + (1. - yy_[:,i]) * e_/phis.E0 )
##                    ss_ = df_ * Eph_
##                    sm_ = np.trapz(ss_, xt_)
##                    df_ /= sm_
                    dem_[:, i] = Eph_ #ss_
##                    pass
                Df_[i,:] = df_
                df_ /= np.max(np.abs(df_))
                dfm_[i,:] = df_
                eav[i] = e_ - e_ / (1. + (1. - cav_[i]) * e_/phis.E0 )
            fig_ +=1
            xxp.xtable_polar(ee_[ixe], xt_, dfm_[ixe,:], gr_name_ + "_directrissa")
            gsave(gr_name_ + "_directrissa")
            fig_ +=1
            xxp.xgraf_plot(ee_, cav_, gr_name_ + "_average", opis_[fext_] )
            gsave(gr_name_ + "_average                     ")

            if fext_ in ['.iv']:
                fig_ +=1
                if fext_ in ['.iv']:
##                    Eph_ = e_ / (1. + (1. - yy_) * e_/phis.E0 )

                    xxp.xtable_plot(ee_[ixe], gg_, dem_[:,ixe], gr_name_ + "_energy", bxlog = False, bylog = True,
                                ylabel = r'$\varepsilon_{\gamma}$', xlabel = r'$\xi$' )
                    opis_['.iv'] = {'legenda':(u'Средняя энергия фотона',),
                     'ylabel':r'$\varepsilon_{\gamma}, эВ$', 'bxlog': True,
                     'bylog':True, 'xlabel':r'$\varepsilon_{\gamma}, эВ$', 'place':'upper left'}
                    xxp.xgraf_plot(ee_, eav, gr_name_ + "_ee_average", opis_[fext_] )
                    gsave(gr_name_ + "_average")
            if fext_ in ['.cv'] :
                fig_ +=1
                xxp.xtable_plot(ee_[1:ne_:(ne_//20+1)], xt_, Df_,gr_name_ + "_energy", bxlog = False, bylog = False,
                            xlabel = r'$cos(\theta)$', ylabel = r' ' )
##                xxp.xtable_plot(ee_, gg_, dem_, fig_, bxlog = False, bylog = True,
##                                ylabel = r'$\varepsilon_{\gamma}$', xlabel = r'$\gamma$' )
                pass
        elif fext_ in ['.526','.527','.555','.516']:

            gg_ = np.logspace(-12, 0, nR_-1)
            gg_ = np.insert(gg_,0,0.)
            if fext_ in ['.527']:
                gg_ = np.linspace(0.,1.0, nR_)

            yy_ = np.power(10, rr_)
            if fext_ in ['.516']:
                ip_ = ee_ > 2* phis.E0
                ee_ = ee_[ip_]
                yy_ = yy_[:, ip_]
                gg_ = gg_[1:]
                yy_ = yy_[1:, :]


            fig_ += 1
            if fext_ in ['.527']:
                xxp.xtable_plot(ee_[ixe], gg_, yy_[:,ixe], gr_name_+ '_table',
                            ylabel = xproc_[fext_]['ylabel'], xlabel = xproc_[fext_]['xlabel'],
                            bxlog = False )
            else:

                xxp.xtable_plot(ee_[ixe], gg_, yy_[:,ixe], gr_name_+ '_table',
                                ylabel = xproc_[fext_]['ylabel'], xlabel = xproc_[fext_]['xlabel'] )
            gsave(gr_name_+ '_table')

            if fext_ in ['.526']:
                yy_ -= 1.

                nn_ = nR_*2
                tt_ = np.linspace(-1, 1, nn_)
                hh_ = 2. / (nn_ - 1)
                xt_ = tt_ + hh_ /2.
                xt_ = xt_[:-1]
                dfm_ = np.zeros((len(ee_), nn_ - 1))
                for i, e_ in enumerate(ee_):
                    dd_ = np.interp(tt_, yy_[:,i], gg_)
                    df_ = np.diff(dd_)/hh_
                    if 0:
                        df_ /= np.max(abs(df_))
                    dfm_[i,:] = df_
                fig_ += 1
                xxp.xtable_polar(ee_[ixe], xt_, dfm_[ixe,:], gr_name_+ "_directrissa")
                gsave(gr_name_ + "_directrissa")

            cav_ = np.trapz(yy_, gg_, axis = 0)
            fig_ += 1
            xxp.xgraf_plot(ee_, cav_, gr_name_+'_average', opis_[fext_] )
            gsave(gr_name_+ '_average')
    xxp.xshw()
    return fig_



def read_file(fig_):
    """
    """
    matFile= askopenfilename(filetypes = ftypes,initialdir = idir)

    fext_=os.path.splitext(matFile)[-1]

    plot_file(matFile,fig_)


def create_parser():
    parser = argparse.ArgumentParser(
         prog='show_table.py',
         formatter_class=argparse.RawDescriptionHelpFormatter,
         fromfile_prefix_chars='@',
         description=textwrap.dedent('''\
   Программа для графического вывода информации  хранящейся в файлах
   подготовленных модулем  построения энергетических и угловых распределений
   фотонов и электронов при их взаимодействии с веществом
   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
       Пример 1:
            show_table.py -с Al Air -e 555 xer
            Будут выведены графики для файлов
                   .\\mat-Al\\electron\\xtbl.555
                   .\\mat-Al\\electron\\xtbl.xer
                   .\\mat-Air\\electron\\xtbl.555
                   .\\mat-Air\\electron\\xtbl.xer
       Пример 2:
            show_table.py -с comp -e 23
            Будtет выведен набор графиков для файлов
                    .\\mat-comp\\electron\\xtbl.23
                    .\\mat-comp\\photon\\xtbl.23
        Пример 3:
            show_table.py -с Fe pena -e 527 -f
            Будут созданы "твёрдые" копии графиков (файлы с раширением "png")
            для файлов
                    .\\mat-Fe\\electron\\xtbl.527
                    .\\mat-pena\\electron\\xtbl.527
            -----------------------------------------------------------------
             '''),
             epilog=phis.epic,
             add_help = False)

    parent_group = parser.add_argument_group (title='Параметры')
    parent_group.add_argument ('--help', '-h', action='help', help='Справка')

    parent_group.add_argument ('--version',
                action='version',
                help = 'Вывести номер версии',
                version = '%(prog)s {}'.format (version))

    parent_group.add_argument ('-c', '--composite', nargs = '+',
            help = 'Список наименований композитов' )
    parent_group.add_argument ('-e', '--extension', nargs = '+',
        help = 'Список расширений файлов в которых сохраняются данные')
    parent_group.add_argument('-f', '--file', action = 'store_true', help = 'сохранять графики в файлах')
    parent_group.add_argument('-l', '--lang', action = 'store_true', help = 'английский вариант')
    return parser


def main(dp):

##    matFile = askopenfilename(filetypes = ftypes, initialdir = db['tab'])
##    fext_ = os.path.splitext(matFile)
##    print(fext_)
##    print(fext_[0].split('/')[-3].split('-')[1])

    dp['fig'] = 1

    plot_file(dp)



if __name__ == '__main__':
    # print(sys.argv[0:])
    try:
        import argparse
        import textwrap

        parser = create_parser()
        namespace = parser.parse_args(sys.argv[1:])

        # print (namespace)

    except ImportError:
        print("версия python < 2.7")

    idir = os.getcwd() #r'c:\ENDF\Projects\Project1'
    # idir = os.path.split(idir)[0] # only for debugging!!!!!!!!
    iSave = namespace.file
    iEnglish_ = namespace.lang
    fig_ = 0
    try:
        if namespace.composite == None and namespace.extension == None:
            matFile= askopenfilename(filetypes = ftypes, initialdir = idir)
            fext_=os.path.splitext(matFile)[-1]

            plot_file(matFile,fig_)

    ##        read_file(fig_)

        else:
            for nmat_ in namespace.composite:
                fname ='mat-' + nmat_
                print(fname)
    ##            fname= os.path.join('result', fname) # for debugging!!!!!!!!
                #matDir= askdirectory(initialdir = idir)
                matDir= os.path.join(idir, fname)

                for (thisdir, subshere, fileshere) in os.walk(matDir): # перечисляет
                    print(('[' + thisdir + ']')) # каталоги в дереве
                    # print(subshere)
                    for fname in fileshere: # вывод файлов в каталоге
                        fext_ = fname.split('.')[1]
        #                fext_=os.path.splitext(matFile_)[-1]
                        if fext_ in namespace.extension:
        #                if fext_ in ['527' ]:
                            path = os.path.join(thisdir, fname) # добавить имя каталога
                            fig_ = plot_file(path, fig_)



    ##    fig_=1
    ##    plot_file(matFile,fig_)
    ##    plt.show()
        if not iSave :xxp.xshw()
    except KeyError:
        print("""\
Произошла непредвиденная ошибка
Возможно данный тип файла не поддерживается""")
        exit(1)
    exit(0)


