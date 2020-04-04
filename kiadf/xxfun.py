#!/usr/bin/python
# -*- coding: utf-8 -*-
## @package xxfun
# Данный модуль предназначен для набора функций и констант
#   используемых в других вычислительных модулях

import re
import os,sys
import math
import numpy as np
##try:
##    import matplotlib.pyplot as plt
##    from mpl_toolkits.mplot3d.axes3d import Axes3D
##except:
##    xGraff=False
##else:
##    xGraff=True

xT={
        'f1':'%4i %4i %4i %4i',
        's1':'# Number row, Number column, Number row of comments,Total number comments',
        'fE':'%6.2f %6.2f %4i %4i',
        'sE':'# Decimal logarithm energy (first point and end point,eV), Number points of energy, Number row of comments',
        'fInf':'%4i %6.2f %8.4e %4i',
        'sInf':'# Atomic number, Atomic massa (gramm), Density (gramm*cm^(-3)), number row of comments',
        'fG':'%6.2f %4i %4i',
        'sG':'% Decimal logarithm second point gamma , Number points of gamma, Number row of comments',
        'sDB':'# ------------------Description of data  -----------------------------------------------------------------------',
        'sDE':'DATA ------------------------------------------------------------------------------------------------------------',
        }


def fixWindowsPath(cmdline):
    """
    change all / to \ in script filename path at front of cmdline;
    used only by classes which run tools that require this on Windows;
    on other platforms, this does not hurt (e.g., os.system on Unix);
    """
    splitline = cmdline.lstrip().split(' ')           # split on spaces
    fixedpath = os.path.normpath(splitline[0])        # fix forward slashes
    return ' '.join([fixedpath] + splitline[1:])      # put it back together


def xxMkDir(drname):
    dirname=fixWindowsPath(drname)
    if not os.path.isdir(os.path.join(os.getcwd(), dirname)):
        os.makedirs(os.path.join(os.getcwd(), dirname))
        #print (os.getcwd())
        #print (dirname)


def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(
            str(sys.executable, sys.getfilesystemencoding( ))
        )
    return os.path.dirname(os.path.abspath(str(__file__, sys.getfilesystemencoding( ))))



# modul xxfun.py
def gavno2num_OLD(ss):
    s1=ss[0:ss.find('.')]
    s2=ss[ss.find('.'):]
    p=re.compile('[+-]')
    m=p.search(s2)
    bg=m.start()
    num=s1+s2[0:bg]+"E"+s2[bg:]
    return num

def gavno2num(ss):
    """
    Translate numeric from ENDF format in usiall format
    For example,
    2.3456986+4 -> 2.3456986E+4
    2.3456986-3 -> 2.3456986E-3
    1.345698-13 -> 2.345698E-13
    """
    ss=ss[::-1]
    p=re.compile('[+-]')
    m=p.search(ss)
    bg=m.start()
    num=ss[0:bg+1]+"E"+ss[bg+1:]
    num=num[::-1]
    return num

def xxCumTrapz(t,f):
    """
    Calculate cumulative integral (trapezium method)

    """
    h=xxDiff(t);
    s=[];
    s.append(0);
    for k in range(len(t)-1):
        sm=s[k];
        st=0.5*h[k]*(f[k+1]+f[k]);
        s.append(sm+st);
    return s


def xxTrapz(t,f):
    h=xxDiff(t);
    st=[0.5*h[k]*(f[k+1]+f[k]) for k in range(len(t)-1)]
    s=sum(st);
    return s

def xxDiff(t):
    d=[t[k+1]-t[k] for k in range(len(t)-1)]
    return d

def xxCalcEav(Eph,Pph):
    """
        вычисляем среднее значение
    """
    EP=Eph[-1]*xxTrapz(Eph,Pph)-xxTrapz(Eph,xxCumTrapz(Eph,Pph))
    return EP

def xxCalcEavF(Eph,Pph):
    """
        вычисляем среднее значение по нормированному распределению
    """
    EP=Eph[-1]-xxTrapz(Eph,Pph)
    return EP

## Функция одномерной линейной интерполяцией
def xxInterp1(a,b,c):
    """
        1-D data linear interpolation
        input data a,b - b(a)
        output - u(c)
    """
#    u=np.interp(c,a,b)
#    return u
    x=list(a);f=list(b);t=list(c)
    M=len(t)
    N=len(x)
    if t[M-1]>x[N-1]:
        x.append(t[M-1])
        f.append(f[N-1])
        N+=1


    if t[0]<x[0]:
        x.insert(0,t[0])
        f.insert(0,f[0])
        N+=1

    u=[]

    it=0;    ix=0;
    while(it<M and ix<N-1):
        if (t[it]-x[ix])*(t[it]-x[ix+1])>0:
            ix+=1
            continue
        else:
            hx=x[ix+1]-x[ix];
            if hx==0.:
                ix+=1
                continue
            u.append((f[ix]*(x[ix+1]-t[it])+f[ix+1]*(t[it]-x[ix]))/hx)
            it+=1;
    return u

def xxInterp_2D(x,y,f,X):
    """ 2-D data linear interpolation
        x,y,f - input parameters

    """
    nX=len(X)
    #nD - number lines, nP - number points in line
    fD=np.array(f);fD=fD.transpose()
    yD=np.array(y);yD=yD.transpose()
    X=np.array(X)
    nP,nD=fD.shape
    xF=np.zeros((nX,nP))
    xY=np.zeros((nX,nP))

    for i in range(nD-1):
        itX=(np.where((X>=x[i])&(X<=x[i+1])))
        nS=np.size(itX)
        if nS>0:
            dx=x[i+1]-x[i]
##            df=fD[:,i+1]-fD[:,i]
##            dy=yD[:,i+1]-yD[:,i]
##            k=df/dx
            y0=np.tile(yD[:,i],(nS,1))
            y1=np.tile(yD[:,i+1],(nS,1))
            f0=np.tile(fD[:,i],(nS,1))
            f1=np.tile(fD[:,i+1],(nS,1))
##            kS=np.tile(k,(nS,1))
            ts=X[itX]
            kS=(ts-x[i])/dx
            tt=np.tile(kS,(nP,1))
            kS=tt.transpose()
            xY[itX,:]=y0*(1-kS)+y1*kS
            xF[itX,:]=f0*(1-kS)+f1*kS

    return xY,xF

def xxCreateTable(x,f,t):
    """
    """
    nDim=f.ndim
    nRow,nCol=x.shape


    pass

## Функция получения таблиц из распределений
def xxGeTable(x, f, t):
    """
    """
    r=[]
    nDim=f.ndim
    nRow,nCol=x.shape
    if nDim==2:


        for ie in range(nRow):
            tt=xxInterp1(x[ie,:],(f[ie,:]),t)
            tt=[math.log10(zx) for zx in tt]
##        try:
##            tt=[math.log10(zx) for zx in tt]
##        except:
##            pass
            r.append(tt)
    else:
##        nRow=len(f)

        for ie in range(nRow):
            tt=xxInterp1(x[ie,:],(f),t)
##            tt=[math.log10(zx) for zx in tt]
            r.append(tt)
##    return np.array(r)
    return r


def xxGeTableBrem(x,f,t):
    """
    """
    r=[]
    nDim=f.ndim
    nRow,nCol=x.shape
    if nDim==2:


        for ie in range(nRow):
            tt=xxInterp1(x[ie,:],(f[ie,:]),t)
##        try:
##            tt=[math.log10(zx) for zx in tt]
##        except:
##            pass
            r.append(tt)
    else:
##        nRow=len(f)

        for ie in range(nRow):
            tt=xxInterp1(x[ie,:],(f),t)
##            tt=[math.log10(zx) for zx in tt]
            r.append(tt)
##    return np.array(r)
    return r



def xxGeTablePhoton(x,f,t):
    """
    """
    r=[]
    nDim=f.ndim
    nRow,nCol=x.shape
    if nDim==2:


        for ie in range(nRow):
            tt=xxInterp1(x[ie,:],(f[ie,:]),t)
            r.append(tt)
    else:
##        nRow=len(f)

        for ie in range(nRow):
            tt=xxInterp1(x[ie,:],(f),t)
##            tt=[math.log10(zx) for zx in tt]
            r.append(tt)
##    return np.array(r)
    return r


def xxTrans(c):
    d=[]
    for i in range(len(c[0])):
        tt=[c[k][i] for k in range(len(c))]
        d.append(tt)
    return d

def e_head(nmElement):
    """ Read head data from ENDF-file
        return 2-dimensional list
    """
    with open(nmElement,'r') as input:
        for i in range(5):
            s=input.readline()
        tp=int(s[49:59])
        for i in range(tp):
            input.readline()
        s=input.readline()
        #nRows=2
        mfC=int(s[29:39])
        mtC=int(s[39:49])
        nRow=int(s[49:59])
        nRows=2;MF=0
        ret=[]
        Shell=[]
        while mfC !=0:
            nRows=nRows+(nRow+0)
            s=input.readline()
            mfC=int(s[29:39])
            mtC=int(s[39:49])
            nRow=int(s[49:59])+1
            ret.append([mfC, mtC, nRow, nRows])
            if mfC==23 and mtC>=534:Shell.append(mtC)
            if MF!=mfC:
                MF=mfC
                ret[-1][3]+=1
                nRows=nRows+1
        del ret[-1]
    Ky=[str(ret[k][0])+str(ret[k][1]) for k in range(len(ret))]
    Vl=[[ret[k][2], ret[k][3]] for k in range(len(ret))]
    D=dict(list(zip(Ky,Vl)))
    #input.close()
    return (D,Shell)

def xxlinspace(a,b,n):
    h=(b-a)/float(n-1)
    t=[a+k*h for k in range(n)]
    return t

def gamma_grid(nG):
    lG=-12
    g=xxlinspace(lG,0,nG-1)
    Gl=[math.pow(10,c) for c in g]
    Gl.insert(0,0.)
    #G1=[0;(10.^Gl)'];
    #G=1-G1;%[1;1-(10.^Gl)'];
    G=[1.0-c for c in Gl]
    #G=[G[c] for c in range(len(G)-1,-1,-1)]
    G.reverse()
    #G=G';
    #G=fliplr(G);
    return G,Gl


def read_23(nmElement,pp):
    """
    Read data from ENDF-file only for Cross Sections
    """
    iPrint=False
    iPrintS=False
    input=open(nmElement,'r')
    for i in range(1,pp[0][3]):
        input.readline()
    ng=11
    k=0
    res=[]
    ShellEb=[]
    while pp[k][0]==23:
        for i in range(1,3):input.readline()
        ss=input.readline()
        if iPrintS:print(ss)
        nk=int(ss[0:11]);nm=int(ss[11:23])
        nk*=nm # This is only for 523 and 528
        if iPrint:print(( pp[k][0],pp[k][1],pp[k][2],nk,nm))
        nrow=nk/6;npurga=(nk-nrow*6)/2
        if iPrint:print(( nrow,npurga))

        for i in range(nrow):
            ss=input.readline()
            if iPrintS:print(ss)
            for j in range(0,3):
                e=gavno2num(ss[2*ng*j:ng*(2*j+1)])
                f=gavno2num(ss[ng*(2*j+1):2*ng*(j+1)])
                #if iPrint:print e,f
                res.append([pp[k][1], e, f])
        if npurga!=0:
            ss=input.readline()
            if iPrintS:print(ss)
            for j in range(0,npurga):
                e=gavno2num(ss[2*ng*j:ng*(2*j+1)])
                f=gavno2num(ss[ng*(2*j+1)+1:2*ng*(j+1)+1])
                #if iPrint:print e,f
                res.append([pp[k][1], e, f])
        input.readline()
        k+=1
        #break
    return res


def GetDummy(MF,MT):
    """
    Using for reading data from ENDF-file
    """
    if MF in (23,27):
        return 1
    elif MF==26 and MT !=528:
        return 5
    elif MF==26 and MT ==528:
        return 4


def read_endf_1d(nmElement,pp,mf,mt):
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


    #global nmIniData
    iPrint=False
    iPrintS=False
    if iPrint:print(( mt,mf))
    with open(nmElement,'r') as input:
        ng=11
        k=0
        res=[]
        ShellEb=[]
        s=str(mf)+str(mt)
        nStrok=pp[s][1]
            #print pp[k]
        if iPrint:print(nStrok)
        for i in range(nStrok):dummy=input.readline()
        dm=GetDummy(mf,mt)
        for i in range(dm):input.readline()
        ss=input.readline()
        if iPrintS:print(ss)
        nk=int(ss[55:66])
        #nk=int(ss[0:11]);#nm=int(ss[11:23])
        #nk*=nm # This is only for 523 and 528
        if iPrint:print(( pp[k][0],pp[k][1],pp[k][2],nk,nm))
        nrow=int(nk/3);npurga=int((nk-nrow*3)/1)
        if iPrint:print((nrow,npurga))
        input.readline() #dummy string
        el=[];fl=[]
        for i in range(nrow):
            ss=input.readline()
            if iPrintS:print(ss)
            for j in range(0,3):
                e=gavno2num(ss[2*ng*j:ng*(2*j+1)]);el.append(e)
                f=gavno2num(ss[ng*(2*j+1):2*ng*(j+1)]);fl.append(f)
                #if iPrint:print e,f
                #res.append([pp[k][1], e, f])
        if npurga!=0:
            ss=input.readline()
            if iPrintS:print(ss)
            for j in range(0,npurga):
                e=gavno2num(ss[2*ng*j:ng*(2*j+1)]);el.append(e)
                f=gavno2num(ss[ng*(2*j+1):2*ng*(j+1)]);fl.append(f)
                #if iPrint:print e,f
        res.append([mt, el, fl])
        input.readline()
    return res

def get_endf_Eb(nmElement, pp, mt):
    """
    Reading binding energy for Subshell
    """

    #global nmIniData
    mf=23
    iPrint=False
    iPrintS=False
    if iPrint:print(( mt,mf))
    with open(nmElement,'r') as input:
        ng=11
        k=0
        res=[]
        ShellEb=[]
        s=str(mf)+str(mt)
        nStrok=pp[s][1]
        for i in range(nStrok):input.readline()
        dm=GetDummy(mf,mt)
        for i in range(dm):input.readline()
        ss=input.readline()
        if iPrintS:print(ss)
        Eb=(ss[0:12]);
    return Eb

def read_endf_2d(nmElement,pp,mf,mt):
    """
    Reading Two-dimensional data from ENDF-file
    For electron:
    23526   Elastic Scattering Cross Sections
    23527   Bremsstrahlung Cross Sections
    23528   Excitation Cross Sections
    23534 ...   Electroionization Subshell Cross Sections
    """

    #global nmIniData
    iPrint=False
    iPrintS=False
    if iPrint:print((mt,mf))
    with open(nmElement,'r') as input:
        ng=11
        k=0
        res=[]
        ShellEb=[]
        Ef=[]
        s=str(mf)+str(mt)
        nStrok=pp[s][1]
        for i in range(nStrok):dummy=input.readline()


        #print self.nmIniData

        dm=GetDummy(mf,mt)
        for i in range(dm):
            dummy=input.readline()
            if iPrintS:print(dummy)

        ss=input.readline()
        if iPrintS:print(ss)
        nE=int(ss[0:11]);
        # only for 527 read data meaning energy loss
        ss=input.readline()
        for ie in range(nE):

            eE=gavno2num(ss[11:23]);nk=int(ss[55:66])
            Ef.append([eE,nk])
            #nk=int(ss[0:11]);nm=int(ss[11:23])
            #nk*=nm # This is only for 523 and 528
            if iPrint:print((pp[k][0],pp[k][1],pp[k][2],nk))
            nrow=int(nk/3);npurga=int((nk-nrow*3)/1);
            if iPrint:print((nrow,npurga))
            el=[];fl=[]
            for i in range(nrow):
                ss=input.readline()
                if iPrintS:print(ss)
                for j in range(0,3):
                    e=gavno2num(ss[2*ng*j:ng*(2*j+1)]);el.append(e)
                    f=gavno2num(ss[ng*(2*j+1):2*ng*(j+1)]);fl.append(f)
                    #if iPrint:print e,f
                    #res.append([pp[k][1], e, f])
            if npurga!=0:
                ss=input.readline()
                if iPrintS:print(ss)
                for j in range(0,npurga):
                    e=gavno2num(ss[2*ng*j:ng*(2*j+1)]);el.append(e)
                    f=gavno2num(ss[ng*(2*j+1)+1:2*ng*(j+1)+1]);fl.append(f)
                    #if iPrint:print e,f
            res.append([mt, eE, el, fl])
            ss=input.readline()
            if iPrintS:print(ss)
    return res

def read_kiam_file_1(nameFL):
    """
    """
    with open(nameFL,'r') as xf:
        """
        """
        hh=[]
        tt=xf.readline()
        nn=tt.split()
        nRow=nn[0]
        nCol=nn[1]
        nKom=nn[3]
        for i in range(nKom):
            dummy=xf.readline()
        d=[]
        for i in range(nRow):
            tt=xf.readline()
            f=tt.split()
            t=[float(c) for c in f]
            d.append(t)
    return d

def read_kiam_file_2(nameFL):
    """
    """
    with open(nameFL,'r') as fIn:
        hh=[]
        for k,line in enumerate(fIn):
            if line.startswith('DATA'):
                break
            else:
                hh.append(line)
        d=[]
        for k,line in enumerate(fIn):
            f=line.split()
            t=[float(c) for c in f]
            d.append(t)
    return d,hh


def read_kiam_file(nameFL):
    """
    """
    with open(nameFL,'r') as fIn:
        hh=[]
        for k,line in enumerate(fIn):
            if line.startswith('DATA'):
                break
            else:
                hh.append(line)
        d=[]
        for k,line in enumerate(fIn):
            f=line.split()
            t=[float(c) for c in f]
            d.append(t)
    return np.array(d),hh



def xxWriteArray(nameFL,d):
    """
    """
    nDim=d.ndim
    if nDim==2:
        nR, nC=d.shape
    else:
        nR=1
        nC=len(d)
    with open(nameFL,'w') as Out:
        Out.write(('%4i %4i\n') % (nR,nC))
        # write data
        for k in range(nR):
             sf=''
             for i in range(nC):
                sf+='%+19.15e ' % (d[i] if nDim==1 else d[k,i])
             sf+='\n'
             Out.write(sf)


def xxReadArray(nameFL):
    """
    """
##    nE,nG=d.shape
    with open(nameFL,'r') as xf:
        tt=xf.readline()
        nn=tt.split()
        nG=int(nn[0])
        nE=int(nn[1])
##        d=np.zeros((nE,nG))
        # read data
        d=[]
        for k,line in enumerate(xf):
            f=line.split()
            t=[float(c) for c in f]
            d.append(t)
    return np.array(d)




def xWrite3_log(nameFL,lE,lG,d,sss,acca='full'):
    """
    """
    nE=len(lE)
    nG=len(lG)
    G0=np.log10(lG[1])
    with open(nameFL,'w') as Out:
        # write heap
        Out.write('{0} \n'.format(xT['f1']))
        Out.write((xT['f1']+'\n') % (nG,nE,2,11))
        Out.write('{0} \n'.format(xT['s1']))
        Out.write('%s \n' % (xT['fE']))
        Out.write((xT['fE']+'\n') % (np.log10(lE[0]),np.log10(lE[-1]),nE,2))
        Out.write('{0} \n'.format(xT['sE']))
        Out.write('{0} \n'.format(xT['fG']))
        Out.write((xT['fG']+'\n')%(G0, nG,5))
        Out.write('{0} \n'.format(xT['sG']))
        Out.write('{0} \n'.format(xT['sDB']))
        Out.write('{0} \n'.format(sss))
        Out.write('{0}(%+19.15f )\n'.format(nE))
        Out.write('{0} \n'.format(xT['sDE']))
        # write data
        for k in range(nG):
            sf='';#str();
            for i in range(nE):
                sf+='%+19.15f ' % (d[i][k])
            sf+='\n';
            Out.write(sf);

def xWrite3_lin(nameFL,lE,lG,d,sss,acca='full'):
    """
    """
    nE=len(lE)
    nG=len(lG)
    with open(nameFL,'w') as Out:
        # write heap
        Out.write('{0} \n'.format(xT['f1']))
        Out.write((xT['f1']+'\n') % (nG,nE,2,8))
        Out.write('{0} \n'.format(xT['s1']))

        Out.write('%s \n' % (xT['fE']))
        Out.write((xT['fE']+'\n') % (np.log10(lE[0]),np.log10(lE[-1]),nE,5))

        Out.write('{0} \n'.format(xT['sE']))
        Out.write('{0} \n'.format(xT['sDB']))
        Out.write('{0} \n'.format(sss))
        Out.write('{0}(%+19.15f )\n'.format(nE))
        Out.write('{0} \n'.format(xT['sDE']))
        # write data
        for k in range(nG):
            sf='';#str();
            for i in range(nE):
                sf+='%+19.15f ' % (d[i][k])
            sf+='\n';
            Out.write(sf);

def xxformat(vv_):
    ex_ = np.trunc(np.log10(vv_))
    ex_ = np.array(ex_, dtype = int)
    mt_ = vv_/np.power(10., ex_)
    se_=('{%2i}' % ex_).lstrip()
    if mt_ == 1.:
        sm_=' 10^'
    else:
        sm_ = '%3.2f\cdot 10^' % mt_
    sl_ = r'$' + sm_ + se_ + ' эВ$'

##    return (mt_, ex_)
    return sl_


def lister(root): # для корневого каталога
    for (thisdir, subshere, fileshere) in os.walk(root): # перечисляет
        print(('[' + thisdir + ']')) # каталоги в дереве
        for fname in fileshere: # вывод файлов в каталоге
            path = os.path.join(thisdir, fname) # добавить имя каталога
            print(path)
if __name__ == '__main__':
    lister(sys.argv[1]) # имя каталога в
# командной строке