#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package interface
# Данный модуль предназначен для подготовки вычисления таблиц распределений
#    - считывает файл parameter.ini
#    - считывает файл compozits

import os,sys
import math
from kiadf import phisconst as phis



## Программа считывает информацию из файла elements
# и создаёт два сортированных массива химических элементов:
#   сортированный по наименованию
#   сортированный по Z

def xxInitElement(name):
    with open(name,'rt') as xFl:
        bE={}
        sN={}
        d={}
        for line in xFl:
            t=line.split()
##            bE[int(t[0])]=[(chr(int(t[1]))+chr(int(t[2]))).strip(),float(t[3]),float(t[4])]
            bE[int(t[0])] = [t[1], float(t[2]), float(t[3])]
    for k in list(bE.keys()):
        sN[bE[k][0]]=int(k)
    return  (bE,sN)


## Класс предназначен для работы с файлом parameter.ini
class Init():
    """
    Initialize the routine's initial data
    """

    avogad=6.022043446928244e+23;
    barns=1.e-24;
    aem=1.660538921;
    sig2mu=avogad*barns;
    xin={}
    DB_dir={}
    bE={}
    sN={}
    ## Программа дла считывания информации из файла parameter.ini
    def __init__(self, nExePath='', nFile=''):
        """
        """
##        self.Z =Z #number element
        if len(nExePath)==0:
            nExePath=os.getcwd()
        xKey=['Emin','Emax','nE','nG','nG_el','nG_ion','nG_br','nG_brtet']
        self.xin['Emin'] = 2.0
        self.xin['Emax'] = 7.0
        self.xin['En'] = 5
        nn=10

        self.xin['nG'] = int(math.pow(2,nn)) # for photons
        self.xin['nX'] = int(math.pow(2,nn)) # for photons
        self.xin['nG_el'] = int(math.pow(2,nn)) # for electrons
        self.xin['nG_ion'] = int(math.pow(2,nn))
        self.xin['nG_br'] = int(math.pow(2,6))
        self.xin['nG_para'] = int(math.pow(2,nn))


        try:
            with open(nFile,'r') as fIn:
                for k,line in enumerate(fIn):
                    t=line.split()
                    if line.startswith('[n'):
                        kl=t[0][1:-1]
                        self.xin[kl]=int(math.pow(2,int(t[1])))
                    elif line.startswith('[E'):
                        kl=t[0][1:-1]
                        self.xin[kl]=int(t[1])
        except IOError:
            print(('Oтсутствует файл {0}. Используются значения по умолчанию.'.format(nFile)))
        self.xin['nE']=int(self.xin['En']*(self.xin['Emax']-self.xin['Emin'])+1)
        self.xin['nX'] = self.xin['nG']


##        self.bE,self.sN=xxInitElement()
        dKey=['gen_elem_data_dir',
            'elem_dir_out',
            'mat_dir_in',
            'mat_dir_out']

        #dirIni=os.path.join('BD','initial_data')
        dirIni=nExePath
##
        dirOut=os.path.join(os.path.join(os.path.dirname(__file__),'BD'))

##        dBB=shelve.open('config.cfg')
##        self.DB_dir=DBB.copy()

##        for k in dBB.keys():
        self.DB_dir[dKey[0]] = os.path.join(nExePath,dirIni)
        self.DB_dir[dKey[1]] = os.path.join(nExePath,dirOut)

        self.bE, self.sN = xxInitElement(os.path.join(os.path.dirname(__file__), 'elements'))
##        self.bE,self.sN=xxInitElement('elements')

## Функция определяет химический элемент
#  по имени или порядковому номеру
    def def_element(self, name = '',Z = 0):
        """
        Initialize the  specified element
        """
        if Z==0:
            Z=(self.sN[name])
        self.xin['Z']=Z
        self.xin['Ro']=self.bE[Z][1]
        self.xin['A'] =self.bE[Z][2] * phis.AEM
        self.xin['Name']=self.bE[Z][0]
        self.xin['elem_dir_IN']=self.DB_dir['gen_elem_data_dir']
        self.xin['elem_dir_OUT']=self.DB_dir['elem_dir_out']
        return self.xin

## Вспомогательный Класс для промежуточного
#  хранения данных о композите
class Material:
    Mat=[]
    NameTable='xtbl'
    Ro=0
    OutName=''

    def __init__(self,ob_):
        self.Mat=ob_['Element']
        self.Ro=ob_['Density']
        self.OutName='mat-'+ob_['Composite']




## Класс для работы с входной информацией о композитах
class Object():
    """
    """

    NameTable='xtbl'


    ## Программа дла считывания информации о композитах
    def __init__(self, nFile, nmEl, flnm,layers):
        self.vv=[]

        with open(layers,'r',encoding='utf-8') as file:
            lay_ = file.readlines()

        lay = [val.split() for val in lay_]
        i=-1
        env=''
##        vt_={}
        try:
            with open(nFile,'r') as fIn:
                for k,line in enumerate(fIn):
                    if line.startswith('['+'Composite'+']'):
                        if i>-1:
                            vt_={ip:{"Composite":env,"Density":Ro,"Element":Mt,"Shell":Sh}}
                            self.vv.append(vt_)

                        i+=1
                        vt_={}
                        Mt=[]
                        Sh=[]
                        t=line.split()
                        env=t[1]
                        env = os.path.splitext(flnm)[0]
                        ip=i
                        ss_=0
    ##                    self.vv[env]=i
                    elif line.startswith('['+'Element'+']'):
                        t=line.split()
                        if t[1] in nmEl.keys():
                            sn_ = t[1]
                        else:
                            sn_ = ''
                            print('В композите  %s - элемент %s ошибочен.' % (env, t[1]))
                        vs_ = float(t[2])
                        ss_ += vs_
                        ion_ = 0
                        if len(t) > 3:
                            t3 = int(t[3])
                            if t3 <= 2 and t3 > 0:
                                ion_ = t3
                        Mt.append([sn_, vs_, ion_])
                    elif line.startswith('['+'Shell'+']'):
                        t=line.split()
                        Sh.append((int(t[1]),ip,t[2]))
                    elif line.startswith('['+'Density'+']'):
                        for i in range(len(lay)):
                            if lay[i][1] == env:
                                Ro = float(lay[i][2])
                        # t=line.split()
                        # Ro=float(t[1])   # сюда надо вставлять правильную плотность
                    elif line.startswith('['+'OUtfile'+']'):
                        t=line.split()
                        self.OutName=(t[1])
                vt_={ip:{"Composite":env,"Density":Ro,"Element":Mt,"Shell":Sh}}
                self.vv.append(vt_)
                for k,mt in enumerate(self.vv):
                    vv_=mt[k]['Element']
                    ss_=0
                    for l,ve_ in enumerate(vv_):
                        ss_+=ve_[1]
                    if math.fabs(1.0-ss_)>1.e-4:
                        print(('Неверно заданы массовые доли композита {0}. Сумма равна {1}'.format(mt[k]['Composite'], ss_)))
                        exit(1)
        except IOError:
            print(('Oтсутствует файл c описанием композита - {0}. '.format(nFile)))
##            exit(2)

    pass


    ## Программа дла создания и записи файла surfaces
    def Sh2file(self,nFile):
        """
        """
        if len(self.vv)==0:
            print ("no data")
            exit(-1)
##        sK=list(self.vv.keys())
        with open(nFile,'w') as Out:
            for k,d in enumerate(self.vv):
                vv_=d[k]["Shell"]
                for xl_ in vv_:
                    Out.write('%4i\t%4i\t%s\n' % (xl_[0],xl_[1],xl_[2]))

    ## Программа дла создания и записи файла materials
    def Mt2file(self,nFile):
        """
        """
        if len(self.vv)==0:
            print ("no data")
            exit(-1)
##        sK=list(self.vv.keys())
        with open(nFile,'w') as Out:
            for k,d in enumerate(self.vv):
                vv_=d[k]["Composite"]
##                Out.write('%s\t%f\n' % (d[k]["Composite"],d[k]["Density"]))
                Out.write('%s\n' % (d[k]["Composite"]))

    ## Программа дла создания и записи файла surfaces
    def Ro2file(self,nFile):
        """
        """
        if len(self.vv)==0:
            print ("no data")
            exit(-1)
##        sK=list(self.vv.keys())
        with open(nFile,'w') as Out:
            for k,d in enumerate(self.vv):
                vv_=d[k]["Shell"]
                ro_ = d[k]['Density']
                for xl_ in vv_:
                    Out.write('%4i\t%9.5f\t%s\n' % (xl_[0], ro_, xl_[2]))



if __name__ == '__main__':
##    xI=xxInit()
    xA=xObject(r'object1.txt')
    xA.Sh2file('surfaces')
    xA.Mt2file('materials')
    pass
