#!/usr/bin/python
# -*- coding: utf-8 -*-
## @package electron
# Данный модуль предназначен для вычисления таблиц распределений для электронов.
# В данном модуле определены классы и функции расчета распределений.
#    Готовятся следующие файлы
#- xtbl.23 – массовые сечения для процессов взаимодействия(см2/г)
#  + Массовое сечение упругого рассеяния (см2/г)
#  + Массовое сечение тормозного излучения (см2/г)
#  + Массовое сечение возбуждения атома (см2/г)
#  + Массовое сечение сечение ионизации атома  (см2/г)
#- xtbl.stp   тормозной путь (г/см2)
#- xtbl.eb    средняя энергия связи на оболочке (эВ)
#- xtbl.528   средняя потеря энергии электрона при процессе возбуждения (эВ)
#- xtbl.555   таблица для розыгрыша энергии вторичного электрона при ионизации атома(эВ)
#- xtbl.526   таблица для розыгрыша косинуса угла электрона при упругом рассеянии.
#- xtbl.527   таблица для розыгрыша энергии фотона при тормозном излучении (эВ)

import os
import math
import time
import numpy as np
#try:
#    import matplotlib.pyplot as plt
#    from mpl_toolkits.mplot3d.axes3d import Axes3D
#except:
#    xGraff=False#else:
#    xGraff=True

from kiadf  import interface as xItf
from kiadf  import xxfun as xox
from kiadf import endf as ken

#import xxplot as xxp
from kiadf import phisconst as phis
#from interface import xxInit


# modul xxfun.py


def graf(f):
    def tmp(*args, **kwargs):
        if xGraff:
           res = f(*args, **kwargs)
           return res
        return 0
    return tmp




## Класс используемый для вычисления электронных распределений
class electron(ken.Kendf):
    """Class for calculating electrons distributions

    """

    nmElData=r"..\initial_data\electrons\endf"
    nmIniData=r"..\initial_data"
    nmOutData=r"..\out\\electrons\\"

    nmElData=r"c:\ENDF\initial_data\electrons\endf"
    nmIniData=r"c:\ENDF\initial_data"
    nmOutData=r"c:\ENDF\out\electrons"


    xFigShow=True
    # if False - calculate always
    xxCalc=False
    xPrintDistrib=False
    xPrintElement=True


    ## Функция инициализации класса electron
    def __init__(self,xin, xion=0):
        """ """
#        import shelve

        self.extf_=['23','526','527','528','555','666','eb','stp','awe', 'xer']
        self.fNl_={}
        self.fNl_['23']=''
        self.fNl_['eb']=''
        self.fNl_['528']=''


        self.Z =xin['Z'] #number element
        self.Ro=xin['Ro']
        self.A =xin['A']
        self.Name=xin['Name']
        self.nmIniData=xin['elem_dir_IN']
        self.nmElData=os.path.join(self.nmIniData,r"electrons")
        self.nmOutData=os.path.join(xin['elem_dir_OUT'],r"electrons")



        self.Emin=xin['Emin']
        self.Emax=xin['Emax'];
        self.nE=xin['nE']
        self.nG_el=xin['nG_el']
        self.fNl_['526']='_' +'%i'%(self.nG_el)
        self.nG_ion=xin['nG_ion']
        self.fNl_['555']='_' +'%i'%(self.nG_ion)
        self.fNl_['666']=self.fNl_['555']
        self.nG_br=xin['nG_br']
        self.fNl_['527']='_' +'%i'%(self.nG_br)
        self.fNl_['awe']='_'+'%i'%(self.nG_ion)+'_'+ '%i'%(self.nG_br)+ '_' +'%i'%(self.nG_el)
        self.fNl_['stp']=self.fNl_['awe']
        self.fNl_['xer']=self.fNl_['awe']
        self.G_el,self.Gl_el=xox.gamma_grid(self.nG_el)

        self.G_br=xox.xxlinspace(0,1,self.nG_br);

        self.G_ion,self.Gl_ion=xox.gamma_grid(self.nG_ion)

        self.E_log=xox.xxlinspace(self.Emin,self.Emax,self.nE);


        self.E=[pow(10,c) for c in self.E_log]

        self.Eph_br_Min=0.1
        self.E2_ion_Min=0.01

        print(('%i'%(self.E_log[0])+ '_' + '%i'%(self.E_log[-1])+
                     '_' +'%i'%(len(self.E_log))+ '_'+'%i'%(self.nG_ion)+
                     '_'+ '%i'%(self.nG_br)+ '_' +'%i'%(self.nG_el)))

        self.Eave_527=[]
        self.Eave_528=[]
        self.Eave_666=[]
#
#        self.DS_526
#        self.SA_526
#
#        self.DS_527
#        self.SA_527
#
#        self.DS_555
#        self.SA_555

        self.F_526=[]
        self.F_527=[]
        self.F_666=[]


        self.StPw_527=[]
        self.StPw_528=[]
        self.StPw_666=[]

        self.StopPath_ALL=[]
        self.OutDir=os.path.join(self.nmOutData,self.Name)
        self.OutDirEndf=os.path.join(self.OutDir,'ENDF')
        self.xfile="e-"+"%03i" %(self.Z)+"_"+self.Name+"_000.endf"
        self.xDirFileElem=os.path.join(self.nmElData,self.xfile)
        ken.Kendf.__init__(self,self.xfile, Elog_ = self.E_log, ion=xion)
        self.xxDir=os.path.join(self.OutDir,
                    '%i'%(self.E_log[0])+ '_' + '%i'%(self.E_log[-1])+
                     '_' +'%i'%(len(self.E_log)))
        # xox.xxMkDir(self.xxDir)
        self.NameFile='el-'+ '%03i'%(self.Z)+ '_'+ self.Name+ '-kiam';
#        self.mas,self.Shell_MT=xox.e_head(os.path.join(self.nmElData,self.xfile))
        self.Shell_MT = self.ElSh_
        self.Nshell = len(self.Shell_MT)


        self.El_NameFile_Out={} # name file for out for elements
#        for k in ('23','526','527','528','555','666','eb','stp','awe'):
#            self.El_NameFile_Out[k]=os.path.join(self.xxDir,self.NameFile+'.'+k)
        self.El_Distrib_Out={} # name file for out for elements
#        for k in ('23','526','527','528','555','666','eb','stp','awe'):
#            self.El_Distrib_Out[k]=os.path.join(self.xxDir,'distrib'+'.'+k)
        self.El_Setka_Out={} # name file for out for elements
#        for k in ('23','526','527','528','555','666','eb','stp','awe'):
#            self.El_Setka_Out[k]=os.path.join(self.xxDir,'Setka'+'.'+k)
        self.El_Middle_Out={} # name file for out for elements
        for k in self.extf_:
            self.El_NameFile_Out[k]=os.path.join(self.xxDir,self.NameFile+self.fNl_[k]+'.'+k)
            self.El_Distrib_Out[k]=os.path.join(self.xxDir,'distrib'+self.fNl_[k]+'.'+k)
            self.El_Setka_Out[k]=os.path.join(self.xxDir,'Setka'+self.fNl_[k]+'.'+k)
            self.El_Middle_Out[k]=os.path.join(self.xxDir,'Eave'+self.fNl_[k]+'.'+k)
        self.s={}


    def read_endf(self,mf,mt):
        """ Middle
        read data from endf file
        """
        #print self.Z,mf,mt
        if mf==23 or mt==528:
            #d=xox.read_endf_1d(self.xDirFileElem,self.mas,mf,mt)
            self.d=self.getVS((mf,mt))
        else:
            #d=xox.read_endf_2d(self.xDirFileElem,self.mas,mf,mt)
            self.d=self.getVS((mf,mt))
        return self.d

    def get_endf_23(self,mf,mt):
        #print( self.Z,mf,mt)
        if mf==23 or mt==528:
            #self.d=xox.read_endf_1d(self.xDirFileElem,self.mas,mf,mt)
            self.d=self.getVS((mf,mt))

            #print self.d
            if mt>528 or self.d[0][2][0].find('0.00')>=0:
                self.d[0][2][0]='1.0E-16';# very importatnt, change 0

            #print self.d
            d = self.d
            ee = [math.log10(float(c)) for c in d[0][1]]
            ec = ee[:];
            ff = [math.log10(float(c)) for c in d[0][2]]
            u = xox.xxInterp1(ec,ff,self.E_log)
            u = [math.pow(10,c)/self.A for c in u];
            #print(ee);print(self.E_log);print(u);
            for k in range(len(u)):
                if self.E_log[k]<ee[0]:
                    u[k] = 0.0
            #um=[0.0*u[k] for k in range(len(u)) if self.E_log[k]<ee[0]];

        return u;

    def get_endf_shell_23(self):
        """
        self.d_23_666 - the sum of all envelope
        """
        self.d_23_666=[0.0 for i in range(self.nE)]

        self.mtx=[]
        for mt in self.Shell_MT:
            u=self.get_endf_23(23,mt)
            #self.d_23_666=[(u[i]+self.d_23_666[i]) for i in range(self.nE)]
            for i in range(self.nE):
                self.d_23_666[i]+=u[i];
            self.mtx.append(u)
        self.mtx.append(self.d_23_666);
        return self.mtx;

    def xox_23(self):
        """
        """
        nmFL=self.El_NameFile_Out['23']
        if os.path.isfile(nmFL) and self.xxCalc:
            t=xox.read_kiam_file_2(nmFL)
            d=np.array(t).transpose()
            d_526=d[1,:];self.d_23_526=np.power(10,d_526)
            d_527=d[2,:];self.d_23_527=np.power(10,d_527)
            d_528=d[3,:];self.d_23_528=np.power(10,d_528)
            d_666=d[4,:];self.d_23_666=np.power(10,d_666)
            d_23=d[1:4,:]

        else:

            d=self.get_endf_shell_23()
            for k_, dd_ in enumerate(self.d_23_666):
                if dd_ == 0.0:
                    self.d_23_666[k_] = 1.E-16

            d_666=[math.log10(c) for c in self.d_23_666]
            self.d_23_526=self.get_endf_23(23,526)
            d_526=[math.log10(c) for c in self.d_23_526];

            self.d_23_527=self.get_endf_23(23,527)
            d_527=[math.log10(c) for c in self.d_23_527]
            self.d_23_528=self.get_endf_23(23,528)
            for k_, dd_ in enumerate(self.d_23_528):
                if dd_ == 0.0:
                    self.d_23_528[k_] = 1.E-16

            d_528=[math.log10(c) for c in self.d_23_528]
            self.d_23=[d_526,d_527,d_528,d_666]
            if False: self.xWrite_23(nmFL, self.d_23)


        d_23=np.array([d_526,d_527,d_528,d_666])
        d_23=np.power(10,d_23)
#        self.d_23=np.array([d_526,d_527,d_528,d_666])

        return d_23.transpose()

    ## Запись таблицы с массовыми сечениями для электрона в файл
    #

    def xWrite_23(self,NameFl,d,acca='full',Density=-1):

        with open(NameFl,'w')as Out:
            # write heap

            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (self.nE,5,2,15))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (self.Emin,self.Emax,self.nE,2))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['fInf']))
            if Density<0:
                Ro=self.Ro
            else:
                Ro=Density

            Out.write((xox.xT['fInf']+'\n') % (self.Z,self.A,Ro,9))
            Out.write('{0} \n'.format(xox.xT['sInf']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            sss="""\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - decimal logarithm of Elastic Scattering Cross Sections per massa(cm^2/gramm)
# 3 column - decimal logarithm of Bremsstrahlung Cross Sections per massa(cm^2/gramm)
# 4 column - decimal logarithm of Excitation Cross Sections per massa(cm^2/gramm)
# 5 column - decimal logarithm of Summary of all Electroionization Subshell Cross Sections per massa(cm^2/gramm)"""
            Out.write('{0} \n'.format(sss))
            Out.write('{0} \n'.format('5(%+19.15f )'))
            Out.write('{0} \n'.format(xox.xT['sDE']))
            # write data

            for k in range(self.nE):
                sf='%+19.15f ' % (self.E_log[k]);#str();
                for i in range(4):
                    sf+='%+19.15f ' % (d[i][k])
                sf+='\n';
                Out.write(sf);
#            Out.close()

    ## Запись таблицы с массовыми сечениями для позитрона в файл
    #
    def xWrite_23p(self,NameFl,d,acca='full',Density=-1, atomassa = -1, atomz = -1):

        with open(NameFl,'w')as Out:
            # write heap

            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (self.nE,5,2,16))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (self.Emin,self.Emax,self.nE,2))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['fInf']))
            if Density < 0:
                Ro=self.Ro
            else:
                Ro=Density

            if atomassa < 0:
                atomassa = self.A

            if atomz < 0:
                atomz = self.Z


            Out.write((xox.xT['fInf']+'\n') % (atomz, atomassa, Ro, 10))
            Out.write('{0} \n'.format(xox.xT['sInf']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            sss="""\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - decimal logarithm of Elastic Scattering Cross Sections per massa(cm^2/gramm)
# 3 column - decimal logarithm of Bremsstrahlung Cross Sections per massa(cm^2/gramm)
# 4 column - decimal logarithm of Excitation Cross Sections per massa(cm^2/gramm)
# 5 column - decimal logarithm of Summary of all Electroionization Subshell Cross Sections per massa(cm^2/gramm)
# 6 column - decimal logarithm of Annihilation of pozitron per massa(cm^2/gramm)"""
            Out.write('{0} \n'.format(sss))
            Out.write('{0} \n'.format('6(%+19.15f )'))
            Out.write('{0} \n'.format(xox.xT['sDE']))
            # write data

            for k in range(self.nE):
                sf='%+19.15f ' % (self.E_log[k]);#str();
                for i in range(5):
                    sf+='%+19.15f ' % (d[i][k])
                sf+='\n';
                Out.write(sf);
#            Out.close()


    ##  Вычисление таблицы распределения для упругого рассеяния электронов
    def xox_526(self):
        """
        Calculate table for Elastic Scattering
        """
        SAm=np.tile(self.d_23_526,(self.nG_el,1)).transpose()
        nmFlS=self.El_Setka_Out['526']
        nmFlD=self.El_Distrib_Out['526']
        if os.path.isfile(nmFlS) and os.path.isfile(nmFlD) and self.xxCalc:
            cs=xox.xxReadArray(nmFlS)
            d=xox.xxReadArray(nmFlD)
            xcF=d.transpose()

        else:
            DEL=1.0e-12
            u=self.read_endf(26,526)
            n=len(u)
            e=[]
            mt=[]
            cs1=np.logspace(-12,math.log10(2),self.nG_el-1)
            cs1=np.insert(cs1,0,0.0)
    #        cs1=np.logspace(-12,math.log10(2),100)
            cs2=2.-cs1
            cs=np.union1d(cs1,cs2)
            ics=(cs==0.)
#            cs[ics]=10**(-16)

            cs=cs2[::-1]
            cs[0]=0.
            cs[-1]=2.
            if self.xPrintDistrib:
                xox.xxWriteArray(nmFlS,cs)

            Ncs=len(cs)
#            xcF=(-16.)*np.ones((self.nE,Ncs))
            xcF=np.zeros((self.nE,Ncs))



    #        self.d_526=np.zeros((self.nE,self.nG_el))
            st_=[]
            for k in range(n):
                e.append(float(u[k][1]));
                vg=[float(c) for c in u[k][2]]
                vz=[float(c) for c in u[k][3]]
                cziz=xox.xxCumTrapz(vg,vz)
                if cziz[-1]<1:
                    cziz.append(1.)
                    vg.append(1.)
    #            else:
    #                cziz[-1]=1.
    #                vg[-1]=1.

                cziz=[c/cziz[-1] for c in cziz]
                vg=[x+1. for x in vg]
    #            if math.fabs(1-cziz[-1])>DEL:
    #                vg.append(1.0)
    #                cziz.append(1.0)
                t=xox.xxInterp1(vg,cziz,cs)
#                t2=np.interp(cs,vg,cziz)
    #            gdc=[t[k]+1 for k in range(1,self.nG_el)]
                mt.append(t)
                dt=np.array(mt).transpose()
            e_log=[math.log10(c) for c in e]
            for ic,cc in  enumerate(cs[1:]):
                xt=np.interp(self.E_log, e_log, np.log10(dt[ic+1,:]))
                xt=np.power(10.,xt)
                xcF[:,ic+1]=xt

            xcF*=SAm
            self.DS_526=xcF
            if self.xPrintDistrib:
                xox.xxWriteArray(nmFlD,xcF.transpose())

        self.Stk_526=cs
        return xcF,SAm

    def xWrite_526(self,nameFL,d,acca='full'):
        """ write 526 data"""

        with open(nameFL,'w') as Out:
            # write heap
            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (self.nG_el,self.nE,2,11))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (self.Emin,self.Emax,self.nE,2))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['fG']))
            Out.write((xox.xT['fG']+'\n')%(math.log10(self.Gl_el[1]), self.nG_el,5))
            Out.write('{0} \n'.format(xox.xT['sG']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            sss='# Output: distribution of log10(1+cos(tet))'
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+19.15f )\n'.format(self.nE))
            Out.write('{0} \n'.format(xox.xT['sDE']))
            # write data

            # write heap
            for k in range(self.nG_el):
                sf='';#str();
                for i in range(self.nE):
                    sf+='%+19.15f ' % (d[i][k])
                sf+='\n';
                Out.write(sf);
#            Out.close()
## Вычисление таблиц для тормозного излучения

    def xox_527(self):
        """
         Calculate table for Bremsstrahlung
        """
        SAm=np.tile(self.d_23_527,(self.nG_br,1)).transpose()
        nmFlS=self.El_Setka_Out['527']
        nmFlD=self.El_Distrib_Out['527']
        if os.path.isfile(nmFlS) and os.path.isfile(nmFlD) and self.xxCalc:
            d=xox.xxReadArray(nmFlS)
            xsEph=d.transpose()
            xsD=xox.xxReadArray(nmFlD)
#            xsD=d.transpose()
        else:

            u=self.read_endf(26,527)
            n=len(u);
            e=[];
            pEph=list()
            Emid=[]
            nEph=self.nG_br
            xsD=np.zeros((self.nE,nEph))
            xsEph=np.zeros((self.nE,nEph))
            for ie,ee in  enumerate(self.E):
                xsEph[ie,:] = np.logspace(math.log10(self.Eph_br_Min),math.log10(ee),nEph)
            if self.xPrintDistrib:
                xox.xxWriteArray(nmFlS,xsEph)

            eEndf = [float(u[k][1]) for k in range(n)]
            pE = []
            pFx = []
            mEendf_ = []
            mPendf_ = []
            mCumPendf = []
            mT_ = []
            xxEav = []
            fig_ = 0
            op_ = {'bxlog': False, 'bylog': True,
                    'tpline1':'b-o', 'tpline2':'r-x'}
            tEv_ = []
            xEv_ = []
            pG = np.tile(self.G_br, (len(eEndf), 1))
            pF = np.zeros((len(eEndf), len(self.G_br)))
            for k,e in enumerate(eEndf):
                Eph = [float(c) for c in u[k][2]]
                mEendf_.append(Eph)
                Pph = [float(c) for c in u[k][3]]
                mPendf_.append(Pph)
                ## вычисляем среднюю энергию
                EP = xox.xxCalcEav(Eph,Pph)
                Emid.append(EP)
                ## получаем кумулятивную функцию распределения
                cP = xox.xxCumTrapz(Eph,Pph)
                cP_end = cP[-1]
                cP = [zc/cP[-1] for zc in cP]
                mCumPendf.append(cP)
                ## аппроксимируем функцию распределения на сетку по гамме
                tt=xox.xxInterp1(cP,Eph,self.G_br)
                tt_ = np.interp(self.G_br, cP, Eph)
                pF[k,:] = tt_
                tEv_.append(np.trapz(tt_, self.G_br))
                xxEav.append(xox.xxTrapz(self.G_br, tt))


                phEl = xox.xxlinspace(math.log10(self.Eph_br_Min),math.log10(Eph[-1]),nEph)
                phE = [math.pow(10,c) for c in phEl]
    #            xP=xox.xxInterp1(Eph,cP,phE)
                ## создали сетку по энергии и на неё аппроксимируем функцию распределения
                xP=xox.xxInterp1(tt,self.G_br,phE)
                xEv_.append(np.trapz(phE, xP))


                pE.append(phE)
                pFx.append(xP)

            if False:
               xG, xFl = xox.xxInterp_2D(np.log10(eEndf),pG,np.log10(pF),self.E_log)
            else:
               xFl = np.zeros((len(self.E_log),len(self.G_br)))
               eldf_ = np.log10(eEndf)
               plf_ = np.log10(pF)

               for ig_, gg_ in enumerate(self.G_br):
                   tt_ = np.interp(self.E_log, eldf_, plf_[:,ig_] )
                   xFl[:,ig_] = tt_

                   pass

            xF = np.power(10,xFl)
            xG = self.G_br

            for ie,ee in  enumerate(self.E):
                if  max(xF[ie,:])>0. :
                   xP = np.interp(xsEph[ie,:], xF[ie,:], xG)
                   xsD[ie,:]=xP


            Eave_527 = np.power(10, np.interp(self.E_log, np.log10(eEndf), np.log10(Emid)))
            self.Eave_527=[]
            for ie,ee in  enumerate(self.E):
                et_ = xsEph[ie,-1] - np.trapz(xsD[ie,:],xsEph[ie,:])
                self.Eave_527.append(et_)

            SAm=np.tile(self.d_23_527,(self.nG_br,1)).transpose()
            xsD *= SAm
            if self.xPrintDistrib:
                xox.xxWriteArray(nmFlD,xsD)
        self.Stk_527=xsEph
        return xsD,SAm





    def xWrite_527(self,nameFL,d,acca='full'):
        """ write 527 data for element """
        with open(nameFL,'w') as Out:
            # write heap
            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (self.nG_br,self.nE,2,8))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (self.Emin,self.Emax,self.nE,5))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            sss='# Output: distribution of logarithm energy of photons'
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+19.15f )\n'.format(self.nE))
            Out.write('{0} \n'.format(xox.xT['sDE']))
            # write data

            for k in range(self.nG_br):
                sf='';#str();
                for i in range(self.nE):
                    sf+='%+19.15f ' % (d[i][k])
                sf+='\n';
                Out.write(sf);


    def xox_528(self):
        """
            excitation
        """
        d=self.read_endf(26,528)
        ee=[math.log10(float(c)) for c in d[0][1]]
        ec=ee[:];
        ff=[math.log10(float(c)) for c in d[0][2]]
        d_528=xox.xxInterp1(ec,ff,self.E_log)
        self.Eave_528=[math.pow(10,c) for c in d_528]
        self.d_528=np.array(d_528)
#        self.d_528.append(d_528)
        s="""\
# 1 column - decimal logarithm of Energy, (eV)
# 2 column - decimal logarithm of Loss Excitation Energy, (eV)"""
        self.s['528']=s

#        self.xWrite_DE(self.El_NameFile_Out['528'],self.E_log,self.d_528[:],s)

        d_528=np.array(self.Eave_528)*np.array(self.d_23_528)
        return d_528

    ##    Calculate Ionization's Sigma
    #     Calculate sum density of probability distribution of secondary electron energy
    #     Calculate probability distribution of secondary electron energy
    #     Calculate middle loss Energy
    #     Calculate Binding Energy
    #            1. loading the density of probability distribution f(x);
    #            2. cumulative integrating the f(x) for obtaining the probability distribution F(x);
    #            3. solving the equation F(x)=g (g is uniformly distributed on (0,1) random number)
    #                for construction of function x=F^-1(g) for samling the x.


    def xox_555(self):
        """ Calculate Ionization's Sigma
            Calculate sum density of probability distribution of secondary electron energy
            Calculate probability distribution of secondary electron energy
            Calculate middle loss Energy
            Calculate Binding Energy
            1. loading the density of probability distribution f(x);
            2. cumulative integrating the f(x) for obtaining the probability distribution F(x);
            3. solving the equation F(x)=g (g is uniformly distributed on (0,1) random number)
                for construction of function x=F^-1(g) for samling the x.
        """
        SAm=np.tile(self.d_23_666,(self.nG_ion,1)).transpose()
        nmFlS=self.El_Setka_Out['555']
        nmFlD=self.El_Distrib_Out['555']
        if os.path.isfile(nmFlS) and os.path.isfile(nmFlD) and self.xxCalc:
            d=xox.xxReadArray(nmFlS)
            xsE2=d.transpose()
            xsD=xox.xxReadArray(nmFlD)
            t=xox.read_kiam_file_2(self.El_NameFile_Out['eb'])
            d=xox.xxTrans(t)
            self.oEb=d[1][:]


        else:

            d=self.get_endf_shell_23()
            SigALL=d[self.Nshell]
            for k_, dd_ in enumerate(SigALL):
                if dd_ == 0.0:
                    SigALL[k_] = 1.E-16

            Sig=d[0:-1]
            ##  self.Kf - koefficient for sigm (sigm(k)/sum(sig(i))
            self.Kf=[[Sig[i][j]/SigALL[j]  for j in range(len(SigALL))]for i in range(len(Sig))];
            xKf=np.array(self.Kf)
            oEb=np.zeros((self.nE))

            self.Res=[[0.0 for k in range(self.nG_ion)]for i in range(self.nE)];

            Eb_=self.getEb()
            Eb=[]
            for ik,mt in enumerate(self.Shell_MT):  # cycle for shell
                # binding energy ez[] and Ez
                Ez=Eb_[mt]

                for k in range(self.nE):
                    oEb[k]+=Ez*self.Kf[ik][k];

                Eb.append(Ez);


            self.Eave_666=[0.0 for i in range(self.nE)]
            nE2=self.nG_ion
            xsD=np.zeros((self.nE,nE2))
            esD=np.zeros((len(self.Shell_MT),self.nE,nE2))
            xsE2=np.zeros((self.nE,nE2))
            self.d_555=np.zeros((self.nE,self.nG_ion))
            for ie,ee in  enumerate(self.E):
                #e2=ee/2+np.interp(ee,self.E_log,oEb)
                e2=ee/2
                cs1=np.linspace(math.log10(self.E2_ion_Min),math.log10(e2),nE2)
                cs1=np.power(10,cs1)
                cs2=e2-cs1
                cs=np.union1d(cs1,cs2)
                ics=(cs==0.)
                cs[ics]=10**(-16)
#                cs+=oEb[ie]
                xsE2[ie,:]=cs1

            if self.xPrintDistrib:
                xox.xxWriteArray(nmFlS,xsE2)
            Ff_=[]
            Gion=self.G_ion
            #Gion[0]=10**(-16)

            for ik,mt in enumerate(self.Shell_MT):  # cycle for shell
                u=self.read_endf(26,mt);
                nE=len(u);
                e0=[float(u[k][1]) for k in range(nE)]
                ff_=[]
                Emid=[]
                pF=np.zeros((len(e0),len(self.G_ion)))
                pG=np.tile(self.G_ion,(len(e0),1))

                for k,xe in enumerate(e0):     # cycle for energy for shell in ENDF
                    Eph=[float(c) for c in u[k][2]]; # without  binding energy
                    Pph=[float(c) for c in u[k][3]];
                    cS_=np.array(xox.xxCumTrapz(Eph,Pph));
                    cS_/=cS_[-1]

                    sK_=xox.xxInterp1(cS_,Eph,self.G_ion);
                    # calc average energy
                    Em = Eph[-1]*xox.xxTrapz(Eph,Pph)-xox.xxTrapz(Eph,xox.xxCumTrapz(Eph,Pph))
                    Em = xox.xxCalcEav(Eph,Pph)
                    Emid.append(Em)
                    pF[k,:] = sK_
                    ff_.append((e0[k],np.array(Eph),np.array(Pph),cS_,sK_ ))

                if True:
                    xFl = np.zeros((len(self.E_log),len(self.G_ion)))
                    eEndf = np.array(e0)
                    eldf_ = np.log10(eEndf)
                    plf_ = np.log10(pF)

                    for ig_, gg_ in enumerate(self.G_ion):
                        tt_ = np.interp(self.E_log, eldf_, plf_[:,ig_] )
                        xFl[:,ig_] = tt_

                    xF=np.power(10.,xFl)
                    xG = self.G_ion
                else:
                    xG,xF=xox.xxInterp_2D((e0),(pG),(pF),self.E)

                for ie,ee in  enumerate(self.E):
                    if  max(xF[ie,:])>10**-16:
                        xP = np.interp(xsE2[ie,:], xF[ie,:], xG)
                        xP = np.array(xP)
                        xP /= xP[-1]
                        xsD[ie,:] += xP * xKf[ik,ie]
                        esD[ik,ie,:] = xP

                e_log = np.log10(e0)
                Emid_log = np.log10(Emid)
                xEav = xox.xxInterp1(e0,Emid,self.E)
                self.Eave_666 = [self.Eave_666[j] + xEav[j]*self.Kf[ik][j] for j in range(self.nE)]

                Ff_.append(ff_)
            Gip = np.array(self.G_ion)
            self.d_555 = xox.xxGeTable(xsD, xsE2, Gip)
            dRc = np.power(10, self.d_555)
            dRc = np.fliplr(dRc)

            E2_ave = []
            #Gip=Gip[::-1]
            for ie in range(self.nE):
                ss = xox.xxTrapz(self.Gl_ion,dRc[ie,:])
                E2_ave.append(ss)


            E2ave = np.array(E2_ave)
            xEb = np.tile(oEb,(self.nG_ion,1)).transpose()
            xE = np.tile(self.E,(self.nG_ion,1)).transpose()


            s="""\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - Binding Energy, eV"""
            self.s['eb'] = s
            self.oEb = oEb
            xsD *= SAm
            if self.xPrintDistrib:
                xox.xxWriteArray(nmFlD,xsD)
        dEb = np.array(self.oEb) * np.array(self.d_23_666)
        self.Eave_666 = E2_ave + oEb
        self.Stk_555 = xsE2
        return xsD, SAm, dEb

    def xCalcTable(self):
        """
        """
        u_23 = self.xox_23()
        Sig_23 = u_23.transpose()

        D_ion, Sig_ion, u_Eb = self.xox_666()
        u_527 = self.xox_527()
        u_526 = self.xox_526()
        u_528 = self.xox_528()


    def xWrite_XXX(self,nameFL,d,sss,acca='full'):
        with open(nameFL,'w') as Out:
            # write heap
            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (self.nG_ion,self.nE,2,11))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (self.Emin,self.Emax,self.nE,2))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['fG']))
            Out.write((xox.xT['fG']+'\n')%(math.log10(self.Gl_ion[1]), self.nG_ion,5))
            Out.write('{0} \n'.format(xox.xT['sG']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+19.15f )\n'.format(self.nE))
            Out.write('{0} \n'.format(xox.xT['sDE']))
            # write data
            for k in range(self.nG_ion):
                sf='';#str();
                for i in range(self.nE):
                    sf+='%+19.15f ' % (d[i][k])
                sf+='\n';
                Out.write(sf);



    def xox_StopPath(self):
        """

        """
        nmFlEawe = self.El_Setka_Out['awe']
        nmFlStp = self.El_Distrib_Out['stp']
        if os.path.isfile(nmFlEawe) and os.path.isfile(nmFlStp) and self.xxCalc:
            d = xox.xxReadArray(nmFlEawe)
            d = d.transpose()
            d = xox.xxReadArray(nmFlStp)
            xcF = d.transpose()
        else:

            xRe = list(range(self.nE))
            self.StPw_527 = [self.Eave_527[i] * self.d_23_527[i] for i in xRe]
            self.StPw_528 = [self.Eave_528[i] * self.d_23_528[i] for i in xRe]
            self.StPw_666 = [self.Eave_666[i] * self.d_23_666[i] for i in xRe]
            s="""\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - decimal logarithm of stopping power for Ionization, (ev*cm^2/g)
# 3 column - decimal logarithm of stopping power for Excitation, (ev*cm^2/g)
# 4 column - decimal logarithm of stopping power for Bremsstrahlung, (ev*cm^2/g)"""
            self.s['xer']=s
            StPw=np.array([self.StPw_666,self.StPw_528,self.StPw_527])
            StPhl =[math.log10(self.StPw_527[i]+self.StPw_528[i]+self.StPw_666[i]) for i in xRe]
            El=xox.xxlinspace(self.Emin,self.Emax,self.nE*2)
            E=[math.pow(10,c) for c in El]
            xStPh=xox.xxInterp1(self.E_log,StPhl,El)
            StPh = [math.pow(10,c) for c in xStPh]
            StPh = [1.0/c for c in StPh]
            E.insert(0,0.0)
            StPh.insert(0,0.0)
            StPh = xox.xxCumTrapz(E,StPh)
            El.insert(0, 0.0)
            StPh = xox.xxInterp1(El, StPh, self.E_log)
            StPh = [math.log10(c) for c in StPh]
            self.StPh = np.array(StPh)
            s="""\
# 1 column - decimal logarithm of Energy, (eV)
# 2 column - decimal logarithm of Stopping Path, (g/cm^2)"""
            self.s['stp'] = s

            lEave_527=[math.log10(c) for c  in self.Eave_527]
            lEave_528=[math.log10(c) for c  in self.Eave_528]
            lEave_666=[math.log10(c) for c  in self.Eave_666]
            self.lEave=[lEave_666,lEave_528,lEave_527]
            s="""\
# 1 column - decimal logarithm of Energy (eV)
# 2 column - decimal logarithm of average loss of Energy for Ionization, (ev)
# 3 column - decimal logarithm of average loss of Energy for Excitation, (ev)
# 4 column - decimal logarithm of average loss of Energy for Bremsstrahlung, (ev)"""
            self.s['awe']=s
        self.lEave=np.array(self.lEave)

        return self.StPh, StPw.transpose()



    def xWrite_DE(self,nameFL,e,d,sss,acca='full'):
        """ write 1D data"""
        nc=sss.count('\n')-1
#        d.insert(0,e)
#        d=[e,d]
#        d=np.array(d)
        ln=2
        le=len(e)
        with open(nameFL,'w') as Out:
            # write heap

            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (le,ln,2,nc+9))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (e[0],e[-1],le,nc+6))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+19.15f )\n'.format(ln))
            Out.write('{0} \n'.format(xox.xT['sDE']))

            # write data
            for k,dv in enumerate(d):
                 sf='%+19.15f %+19.15f\n' % (e[k],dv)
#                 for i in range(ln):
#                    sf+='%+19.15f ' % (d[i][k])
#                 sf+='\n'
                 Out.write(sf)

    def xWrite_DE2(self,nameFL,e,d,sss,acca='full'):
        """ write 2D data"""
        nc=sss.count('\n')-1
        d.insert(0,e)
        ln=len(d)
        le=len(e)
        with open(nameFL,'w') as Out:
            # write heap

            Out.write('{0} \n'.format(xox.xT['f1']))
            Out.write((xox.xT['f1']+'\n') % (le,ln,2,nc+9))
            Out.write('{0} \n'.format(xox.xT['s1']))
            Out.write('%s \n' % (xox.xT['fE']))
            Out.write((xox.xT['fE']+'\n') % (e[0],e[-1],le,nc+6))
            Out.write('{0} \n'.format(xox.xT['sE']))
            Out.write('{0} \n'.format(xox.xT['sDB']))
            Out.write('{0} \n'.format(sss))
            Out.write('{0}(%+19.15f )\n'.format(ln))
            Out.write('{0} \n'.format(xox.xT['sDE']))

            # write data
            for k in range(le):
                 sf=''
                 for i in range(ln):
                    sf+='%+19.15f ' % (d[i][k])
                 sf+='\n'
                 Out.write(sf)







def sigma_annig(T):
    """
    k=T/E0 + 1
    """
    ZZ_  =1
    T = np.array(T)
    k = T/phis.E0 + 1
    cg_ = ZZ_ * np.pi * phis.Re2 / (k + 1) * ((k ** 2 + 4 * k + 1) / (k ** 2 - 1) * np.log(k + np.sqrt((k ** 2 - 1)))
     - ((k + 3) / np.sqrt(k ** 2 - 1)))
    return cg_


## Программа для расчета таблиц для композитов
#
def main(xI,Mt,matFile, path):
    """
    программа для расчета таблиц для композитов
    """
#    import annig_pozitron as ang

##    path,nmFile=os.path.split(matFile)
##    os.getcwd()
##
##    NmFile,ExtFile=os.path.splitext(nmFile)
    NmFile=Mt.NameTable
    nE=xI.xin['nE']
    nG_br=xI.xin['nG_br']
    nG_el=xI.xin['nG_el']
    nG_ion=xI.xin['nG_ion']
    d_sig = np.zeros((nE,4))
    out_23p = np.zeros((5, nE))
    d_br = np.zeros((nE,nG_br))
    SSig_br = np.zeros((nE,nG_br))
    d_el=np.zeros((nE,nG_el))
    SSig_el=np.zeros((nE,nG_el))
    d_ion=np.zeros((nE,nG_ion))
    SSig_ion=np.zeros((nE,nG_ion))
    d_ext=np.zeros((nE,))
    d_eb=np.zeros((nE,))
    d_stop=np.zeros((nE,))
    d_awe=np.zeros((nE,3))

#        matFile=os.path.join(path,nfile)
#        Mt=xItf.Material(matFile)
#        NmFile,ExtFile=os.path.splitext(nfile)
    DirOut=os.path.join(path,Mt.OutName,'electron')
    xox.xxMkDir(DirOut)
    FileOut=os.path.join(DirOut, NmFile)+'.'
    spisok=Mt.Mat
    FlExt={'526':'526','527':'527','528':'528','555':'555','eb':'eb',
    '23':'23','awe':'awe','stp':'stp', 'poz':'23p','xer':'xer'}
    aw_ = 0.0
    zz_ = 0.0
    S_sig_annih = 0
#        for i,k in enumerate(Mt.Mat.keys()):
#            p=Mt.Mat[k]
#            name=k
    for i,k in enumerate(spisok):
        name=k[0]
        p=k[1]
        ion = k[2]
        print (name, p, ion)
        xB=xI.def_element(name)
        A=electron(xB, xion=ion)
        aw_ += p * A.A
        zz_ += p * A.Z
        if i == 0:
            Sig_annih = sigma_annig(A.E)
        S_sig_annih += A.Z/A.A
        u_23 = A.xox_23()

        d_sig += p*u_23
        #
        u_555,Sig_ion,u_Eb = A.xox_555()
        d_ion += p*u_555
        SSig_ion += p*Sig_ion
        d_eb += p * u_Eb

        u_526, Sig_el=A.xox_526()
        d_el += p*u_526
        SSig_el += p*Sig_el

        u_527,Sig_br = A.xox_527()
        d_br += p*u_527
        SSig_br += p*Sig_br

        u_528=A.xox_528()
        d_ext+=p*u_528

        u_sp,u_ae=A.xox_StopPath()
        d_awe+=p*u_ae
        d_stop+=p*np.power(10,-u_sp)

    Sig_annih *=S_sig_annih # annihilation
    Sig_annih = np.log10(Sig_annih)

    out_23=np.log10(d_sig.transpose())
    out_23p[:-1,:] = out_23[:,:]
    out_23p[-1,:] = Sig_annih
    A.xWrite_23(FileOut+FlExt['23'], list(out_23), Density = Mt.Ro)
    A.xWrite_23p(FileOut+FlExt['poz'], list(out_23p), Density = Mt.Ro, atomassa = aw_, atomz = zz_)

    d_ext/=d_sig[:,2]
    d_ext=np.log10(d_ext)
    A.xWrite_DE(FileOut+FlExt['528'],A.E_log,list(d_ext),A.s['528'])

    Dbl_526=u_526/Sig_el
    tbl_526=xox.xxGeTable(Dbl_526,A.Stk_526,A.Gl_el)
    tbl_526=np.array(tbl_526)
    tbl_526[:,1:]=np.log10(tbl_526[:,1:])
#    tbl_526=xox.xxGeTable(Dbl_526,np.log10(A.Stk_526),A.Gl_el)
#        s='# Output:  distribution of logarithm energy of scatering electron'
    A.xWrite_526(FileOut+FlExt['526'],list(tbl_526))

    Dbl_527=u_527/Sig_br
#    tbl_527=xox.xxGeTable(Dbl_527,A.Stk_527,A.G_br)
    tbl_527=xox.xxGeTableBrem(Dbl_527,np.log10(A.Stk_527),A.G_br)
#    tbl_527 = np.power(10, tbl_527)

    tbl_527=np.fliplr(tbl_527)
#        s='# Output:  distribution of logarithm energy of scatering electron'
    A.xWrite_527(FileOut+FlExt['527'],tbl_527)


    d_eb/=d_sig[:,3]
    A.xWrite_DE(FileOut+FlExt['eb'],A.E_log,list(d_eb),A.s['eb'])

    Dbl_555=u_555/Sig_ion

#    for i,e in enumerate(A.E):
#        ebm_=np.tile(d_eb[i],A.nG_ion)
#        Dbl_555[i][:]+=ebm_
#    Dbl_555=np.flipud(Dbl_555)
    tbl_555=xox.xxGeTable(Dbl_555,A.Stk_555,A.G_ion)
    tbl_555=np.fliplr(tbl_555)
#    tt_=np.power(10,tbl_555)
#    for i in range(A.nE):
#        for j in range(A.nG_ion):
#            tt_[i][j] +=d_eb[i]
#
#    tbl_555=np.log10(tt_)
#    tbl_555=[tbl_555[i][::-1] for i in range(len(tbl_555))]
    s='# Output:  distribution of logarithm energy of recoil electron'
    A.xWrite_XXX(FileOut+FlExt['555'],tbl_555,s)

    d_stop=-np.log10(d_stop)
    A.xWrite_DE(FileOut+FlExt['stp'],A.E_log,list(d_stop),A.s['stp'])

    A.xWrite_DE2(FileOut+FlExt['xer'],A.E_log,list(np.log10(d_awe).transpose()),A.s['xer'])

    d_awe[:,0]/=d_sig[:,3] # Ionization
    d_awe[:,1]/=d_sig[:,2]  # Excitation
    d_awe[:,2]/=d_sig[:,1]  # Bremsstrahlung
    d_awe=np.log10(d_awe)
    A.xWrite_DE2(FileOut+FlExt['awe'],A.E_log,list(d_awe.transpose()),A.s['awe'])



if __name__ == '__main__':
    Z=6
    xI=xItf.xxInit(nFile = 'xparameter.ini')
    xB=xI.def_element(Z=Z)
    A=electron(xB)

    u_23=A.xox_23()
    u_527=A.xox_527()
    exit(1)
    u_527=A.xox_555()
#    xxp.xshw()
#    u_526=A.xox_526()
#    D_ion,Sig_ion,u_Eb=A.xox_555()

    u_23=u_23.transpose()

    Sig_526=u_23[:,0]
    Sig_527=u_23[:,1]
    Sig_528=u_23[:,2]
    Sig_555=u_23[:,3]
    u_526=A.xox_526()
    u_527=A.xox_527()

    u_528=A.xox_528()
    u_StPath,u_lEave=A.xox_StopPath()


