#!/usr/bin/env python
# -*- coding: utf-8 -*-
## @package xxplot
# Модуль содержит набор функций дял графического представления
# полученных распределений
#


import numpy as np
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.axes3d import Axes3D
except:
    iPlot = False
else:
    iPlot = True
    from matplotlib import rc
    font = {'family': 'Verdana',
            'weight': 'normal'}
    rc('font', **font)

##import matplotlib.pyplot as plt

##iPlot=False

from kiadf import xxfun as xox


iEnglish_ = False

cs = 'kgrbcym'
ss = ['-', '--', '-.', '-d', '.', ':', '-.', ':', '-+']

prm = {'xtl':18, 'ytl':18}

class Carxiv:
    """
    """
    cg_=r'$cos(\theta_{\gamma})$'
    ce_=r'$cos(\theta_{e})$'
    eg_='$E_{\gamma}'



class Xplot:
    """
    """
    fig_=1
    title_="Title"
    xlabel_='x'
    ylabel_='y'
    text_=''
    xaxis_=[0,1]
    yaxis_=[0,1]
    t_=[]
    f_=[]
    def __init__(fg_):
        """
        """
        self.fig_=fg_


def xxformat(vv_):
    ex_ = np.trunc(np.log10(vv_))
    ex_ = np.array(ex_, dtype = int)
    mt_ = vv_/np.power(10., ex_)
    se_=('{%2i}' % ex_).lstrip()
    if mt_ == 1.:
        sm_=' 10^'
    else:
        sm_ = '%3.2f\cdot 10^' % mt_
    if iEnglish_:
        kl_ = ' eV$'
    else:
        kl_ = ' эВ$'
    sl_ = r'$' + sm_ + se_ + kl_

##    return (mt_, ex_)
    return sl_



def xexec(f):
    def tmp(*args, **kwargs):
        if iPlot:
            res = f(*args, **kwargs)    #(args[0],args[1],args[2])
            return res
        return 0
    return tmp

@ xexec
def xxplt(x,y,s):
    return plt.plot(x,y,s)
    pass

@ xexec
def xshw():
    return plt.show()
    pass

@ xexec
def figshow():
    return fig.show()
    pass


@ xexec
def xsave_fig(name_):
    plt.savefig(name_, dpi=300)

@ xexec
def xplot_cs(x_, y_, fig_, dt_):
    """
    """
    print(( len(y_.transpose())))
    fig = plt.figure(fig_, figsize = (8, 8))
    fig.subplots_adjust(bottom = 0.26, right = 0.96, left = 0.14)
    ax=fig.add_subplot(111)
##    for kl in range(len(y_.transpose())):
##        ax.loglog(x_, y_[:,kl], cs[kl%len(ss)]+ss[kl%len(ss)], linewidth=2.0, )
    ax.loglog(x_, y_, dt_.get('line_style' , '-'), linewidth=2.0, )
    legend = dt_.get('legenda', () )
    leg = ax.legend(legend, bbox_to_anchor=(0., -0.37,  1., .102), loc=3,
            ncol=2, mode="expand", borderaxespad=0.)
    for t in leg.get_texts():
        t.set_fontsize('small')
##        ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

##        ax.legend( loc=3,ncol=2,mode="expand", borderaxespad=0.)
    plt.grid(True)
    xlabel_ = dt_.get('xlabel','x')
    xlabel_ = xlabel_ if type(xlabel_) == type('') else xlabel_
    ax.set_xlabel(xlabel_, fontsize = 18, style = 'italic',)
    ylabel_ = dt_.get('ylabel','y')
    ylabel_ = ylabel_ if type(ylabel_) == type('') else ylabel_
    ax.set_ylabel(ylabel_, fontsize = 18, style = 'italic',)
    plt.xticks(fontsize=prm['xtl'])
    plt.yticks(fontsize=prm['ytl'])

    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Сечения процессов')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize=20, fontweight = 'bold')
##    fig.suptitle(tmp_, color = 'k', fontsize = 20, )

@ xexec
def xgraf_plot(x_, y_, ifig_, dt_ ):
    """
    """
    fig = plt.figure( ifig_, figsize = (8, 8))
    fig.subplots_adjust(right = 0.97, bottom = 0.12, left = 0.14)
    ax=fig.add_subplot(111)
##    tt_ = dt_.get('ylabel', 'y')
    xlabel_ = dt_.get('xlabel','x')
    xlabel_ = xlabel_ if type(xlabel_) == type('') else xlabel_
    ax.set_xlabel(xlabel_, fontsize = 18, style = 'italic',)
    ylabel_ = dt_.get('ylabel','y')
    ylabel_ = ylabel_ if type(ylabel_) == type('') else ylabel_
    ax.set_ylabel(ylabel_, fontsize = 18, style = 'italic',)
    bxlog = dt_.get('bxlog', True)
    bylog = dt_.get('bylog', True)
    tpline = dt_.get('tpline', '-')
    if bxlog and bylog:
        ax.loglog(x_, y_, tpline, linewidth = 2.0,)
    elif bxlog:
        ax.semilogx(x_, y_, tpline, linewidth = 2.0, )
    elif bylog:
        ax.semilogy(x_, y_, tpline, linewidth = 2.0, )
    else:
        ax.plot(x_, y_[i], tpline, linewidth = 2.0, )
    if dt_.get('legenda', False):
        leg = ax.legend(dt_['legenda'], loc=dt_['place'], ncol=1, shadow=True, )
##        leg = ax.legend(dt_['legenda'], loc=4, ncol=1, shadow=True, )
    ##    ax.legend(bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
        for t in leg.get_texts():
            t.set_fontsize('medium')
    plt.xticks(fontsize=prm['xtl'])
    plt.yticks(fontsize=prm['ytl'])
##    ax.grid(True)
# Don't allow the axis to be on top of your data
    ax.set_axisbelow(True)
    ax.minorticks_on()
# Customize the major grid
    ax.grid(b=True, which='major', linestyle='-', linewidth='0.75', color='#000040')
# Customize the minor grid
    ax.xaxis.grid(b=True, which='minor',) # linestyle=':', linewidth='0.5', color='#0b0b0b')
    ax.yaxis.grid(b=True, which='minor',)
    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Заголовок')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize = 20, fontweight = 'bold')
    return fig


@ xexec
def xgraf2_plot(x1_, y1_, x2_, y2_, ifig_, dt_):
    """
    """
    fig = plt.figure( ifig_, figsize = (9, 6))
    fig.subplots_adjust(right = 0.97, bottom = 0.12)
    ax=fig.add_subplot(111)
##    tt_ = dt_.get('ylabel', 'y')
##    ax.set_ylabel(dt_.get('ylabel', 'y'), fontsize = 18)
##    ax.set_xlabel(dt_.get('xlabel', 'x'), fontsize = 18, style='italic', weight = 'bold')
    xlabel_ = dt_.get('xlabel','x')
    xlabel_ = xlabel_ if type(xlabel_) == type('') else xlabel_
    ax.set_xlabel(xlabel_, fontsize = 18, style = 'italic',)
    ylabel_ = dt_.get('ylabel','y')
    ylabel_ = ylabel_ if type(ylabel_) == type('') else ylabel_
    ax.set_ylabel(ylabel_, fontsize = 18, style = 'italic',)
    bxlog = dt_.get('bxlog', True)
    bylog = dt_.get('bylog', True)
    tpline1 = dt_.get('tpline1', 'b-')
    tpline2 = dt_.get('tpline2', 'go')
    if bxlog and bylog:
        ax.loglog(x1_, y1_, tpline1, linewidth = 2.0,)
        ax.loglog(x2_, y2_, tpline2, linewidth = 2.0,)
    elif bxlog:
        ax.semilogx(x1_, y1_, tpline1, linewidth = 2.0,)
        ax.semilogx(x2_, y2_, tpline2, linewidth = 2.0,)
    elif bylog:
        ax.semilogy(x1_, y1_, tpline1, linewidth = 2.0,)
        ax.semilogy(x2_, y2_, tpline2, linewidth = 2.0,)
    else:
        ax.plot(x_, y_[i], '-+', linewidth = 2.0, )
    if dt_.get('legenda', False):
        leg = ax.legend(dt_['legenda'], loc=dt_['place'], ncol=1, shadow=True, )
##        leg = ax.legend(dt_['legenda'], loc=dt_['place'], ncol=1, shadow=True, )
        for t in leg.get_texts():
            t.set_fontsize('medium')
    ax.grid(True)
    ax.set_xlim(max(x1_[0], x2_[0]), min(x1_[-1], x2_[-1]))
    ax.set_ylim(min(min(y1_), min(y2_)), max(max(y1_), max(y2_)))
    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Заголовок')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize = 20, fontweight = 'bold')

    return ax

@ xexec
def xgraf_array(xx_, yy_, ifig_, dt_, ):
    """
    """
    if len(xx_) != len(yy_):
        return -1

    fig = plt.figure( ifig_, figsize = (9, 6))
    fig.subplots_adjust(right = 0.97, bottom = 0.12)
    ax=fig.add_subplot(111)
##    tt_ = dt_.get('ylabel', 'y')
##    ax.set_ylabel(dt_.get('ylabel', 'y'), fontsize = 18)
##    ax.set_xlabel(dt_.get('xlabel', 'x'), fontsize = 18, style='italic', weight = 'bold')
    xlabel_ = dt_.get('xlabel','x')
    xlabel_ = xlabel_ if type(xlabel_) == type('') else xlabel_
    ax.set_xlabel(xlabel_, fontsize = 18, style = 'italic',)
    ylabel_ = dt_.get('ylabel','y')
    ylabel_ = ylabel_ if type(ylabel_) == type('') else ylabel_
    ax.set_ylabel(ylabel_, fontsize = 18, style = 'italic',)
    bxlog = dt_.get('bxlog', True)
    bylog = dt_.get('bylog', True)
    for i, xg_ in enumerate(xx_):
        x_ = xx_[i]
        y_ = yy_[i]
        tpline_ = dt_.get('tpline', len(xx_)*'-')[i]
        if bxlog and bylog:
            ax.loglog(x_, y_, tpline_, linewidth = 2.0,)
        elif bxlog:
            ax.semilogx(x_, y_, tpline_, linewidth = 2.0, )
        elif bylog:
            ax.semilogy(x_, y_, tpline_, linewidth = 2.0, )
        else:
            ax.plot(x_, y_[i], tpline_, linewidth = 2.0, )
    if dt_.get('legenda', False):
        leg = ax.legend(dt_['legenda'], loc=dt_['place'], ncol=1, shadow=True, )
    ##    ax.legend(bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
        for t in leg.get_texts():
            t.set_fontsize('medium')
    ax.grid(True)
    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Заголовок')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize = 20, fontweight = 'bold')

@ xexec
def xtable_plot(e_, xx_, yy_, ifig, **dt_):
##def xtable_plot(e_, x_, y_, ifig, bxlog = True, bylog = True,
##         xlabel = '', ylabel = '', title = ''):
    """
    """
    if type(xx_) != type([]) and len(xx_.shape) == 1:
        nR_, nC_ = yy_.shape
        lX_ = len(xx_)
        if lX_ == nR_:
            yy_ =np.transpose(yy_)

    fig = plt.figure( ifig, figsize = (9, 7))
    fig.subplots_adjust(right = 0.7)
    ax=fig.add_subplot(111)
    xlabel_ = dt_.get('xlabel','x')
    xlabel_ = xlabel_ if type(xlabel_) == type('') else xlabel_
    ax.set_xlabel(xlabel_, fontsize = 18, style = 'italic',)
    ylabel_ = dt_.get('ylabel','y')
    ylabel_ = ylabel_ if type(ylabel_) == type('') else ylabel_
    ax.set_ylabel(ylabel_, fontsize = 18, style = 'italic',)

    bxlog = dt_.get('bxlog', True)
    bylog = dt_.get('bylog', True)
    tpline = dt_.get('tpline', '-')
    sl_ =[]
    for i, ee_ in enumerate(e_):
##        sl_ = '%5.2E eV' % (ee_)
        y_ = yy_[i]
        if type(xx_) != type([]) and len(xx_.shape) == 1:
            x_ = xx_
        else:
            x_ = xx_[i]
##        ss_ = xox.xxformat(ee_)
        ss_ = xxformat(ee_)

        ss_ = ss_ if type(ss_) == type('') else ss_
        sl_.append(ss_)
##        tpline = cs[i%len(cs)]+ss[i%len(ss)]
        if bxlog and bylog:
            ax.loglog(x_, y_, tpline, linewidth = 2.0,)
        elif bxlog:
            ax.semilogx(x_, y_, tpline, linewidth = 2.0, )
        elif bylog:
            ax.semilogy(x_, y_, tpline, linewidth = 2.0, )
        else:
            ax.plot(x_, y_, tpline, linewidth = 2.0,)

    ax.legend(sl_, bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
    ax.grid(True)
##    plt.tight_layout()
    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Заголовок')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize=16, fontweight = 'bold')


@ xexec
def xtable_polar(e_, xx_, yy_, ifig, **dt_):
    """
    """
    nR_, nC_ = yy_.shape
    lX_ = len(xx_)
    if lX_ == nR_:
        yy_ =np.transpose(yy_)
    tet_=np.arccos(xx_)
##    tetg_ = np.insert(tet_, 0, -tet_[ ::-1])
    tetg_ = np.append(-tet_[::-1], tet_)
    fig = plt.figure(ifig, figsize=(9,6))
    fig.subplots_adjust(right = 0.7)
    ax=fig.add_subplot(111, polar = True)
##    ax.set_ylabel(xlabel, fontsize = 18)
##    ax.set_xlabel(ylabel, fontsize = 18, style = 'italic', weight = 'bold')


    for i, ee_ in enumerate(e_):
##        sl_ = '%5.2E eV' % (ee_)
        sl_ = xox.xxformat(ee_)
##        sl_ = xxformat(ee_)
        sl_ = sl_ if type(sl_) == type('') else sl_

##        pp_ = np.insert(yy_[i, :], 0, yy_[i, ::-1])
        pp_=np.append(yy_[i,::-1], yy_[i,:])
        ax.plot(tetg_, pp_, '-', linewidth = 2.0, label = sl_,)

    ax.legend(bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
    ax.grid(True)
##    plt.tight_layout()

    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Заголовок')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize=20, fontweight = 'bold')


@ xexec
def xtable_plot3d(e_, xx_, yy_, ifig, **dt_):
##def xtable_plot(e_, x_, y_, ifig, bxlog = True, bylog = True,
##         xlabel = '', ylabel = '', title = ''):
    """
    """
    if type(xx_) != type([]) and len(xx_.shape) == 1:
        nR_, nC_ = yy_.shape
        lX_ = len(xx_)
        if lX_ == nR_:
            yy_ =np.transpose(yy_)

    me, mx = np.meshgrid(e_, xx_)
    fig = plt.figure( ifig, figsize = (9, 7))
    fig.subplots_adjust(right = 0.7)
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    xlabel_ = dt_.get('xlabel','x')
    xlabel_ = xlabel_ if type(xlabel_) == type('') else xlabel_
    ax.set_xlabel(xlabel_, fontsize = 18, style = 'italic',)
    ylabel_ = dt_.get('ylabel','y')
    ylabel_ = ylabel_ if type(ylabel_) == type('') else ylabel_
    ax.set_ylabel(ylabel_, fontsize = 18, style = 'italic',)

    bxlog = dt_.get('bxlog', True)
    bylog = dt_.get('bylog', True)
    tpline = dt_.get('tpline', '-')
    sl_ =[]
    for i, ee_ in enumerate(e_):
##        sl_ = '%5.2E eV' % (ee_)
        y_ = yy_[i]
        if type(xx_) != type([]) and len(xx_.shape) == 1:
            x_ = xx_
        else:
            x_ = xx_[i]
##        ss_ = xox.xxformat(ee_)
        ss_ = xxformat(ee_)

        ss_ = ss_ if type(ss_) == type('') else ss_
        sl_.append(ss_)
        if bxlog and bylog:
            ax.loglog(x_, y_, tpline, linewidth = 2.0,)
        elif bxlog:
            ax.semilogx(x_, y_, tpline, linewidth = 2.0, )
        elif bylog:
            ax.semilogy(x_, y_, tpline, linewidth = 2.0, )
        else:
            ax.plot(x_, y_, tpline, linewidth = 2.0,)

    ax.legend(sl_, bbox_to_anchor = (1.05, 1), loc = 2, borderaxespad = 0.)
    ax.grid(True)
##    plt.tight_layout()
    if dt_.get('title', False):
        tmp_ = dt_.get('title', 'Заголовок')
        title_ = tmp_ if type(tmp_) == type('') else tmp_
        fig.suptitle(title_, color='k', fontsize=16, fontweight = 'bold')




if __name__ == '__main__':
##    t=np.linspace(0,2*np.pi,101)
##    f=np.cos(t)
##    xxplt(t,f,'r-')
##    xxshw()
    x_ = np.logspace(2, 7, 11)

    y_ =np.log10(x_)
     ##    rx_ = np.random.rand(nE_, nG_)
    d_ = {}
    d_['bylog'] = False
    d_['tpline'] = '-o'
    xgraf_plot(x_, y_, 2,  d_)
##    xgraf_plot(x_, y_, 2, saas = d_)
    xshw()

