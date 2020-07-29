#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      PC
#
# Created:
# Copyright:   (c) PC
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import os
import zipfile as z
##import json
import pickle
##import numpy as np


def infa():
    di = {}
    di['O'] = {'dr':'ions_files\\O','0':4, 'shell':[536,537]}
    di['N'] = {'dr':'ions_files\\N','0':3, 'shell':[536,537]}
    with open("ion.json", "w") as write_file:
        json.dump(di, write_file)



def ion_data(elem):
    ss=''
    cdir = os.path.dirname(__file__)
    bd = json.load(open(os.path.join(cdir,"ion.json")))
    print(bd)
    if elem in list(bd.keys()):
##        db[elem] = dd[elem].copy()
        edr = os.path.join(cdir,elem)
##        ss = os.path.join(edr, 'data.json')
        sp = os.path.join(edr, 'data.pkl')
##        dd = json.load(open( os.path.join(edr, 'data.json'))).copy()
##        disg = np.array(json.load(open( os.path.join(edr, 'diffsigma.json'))) )
##        sigma = np.array(json.load(open( os.path.join(edr, 'sigma.json'))))
##        db[elem]['e'] = sigma[:,0]
##        db[elem]['sig'] = sigma[:,1]
##        db[elem]['dsg'] = disg
##        return True
##    else:
##        return False
    return ss, sp

def data_endf(sti, bion, bstr):
    """
        sti -  заряд иона
        bion - словарь с ионами
        bstr - словарь с ENDF
    """
##    sk = str(sti)
##
    for mft in list(bion[sti].keys()):
##        mt = int(smt)
        if mft[0] == 23:
            vv = [bion[sti][mft] * tt for tt in bion['sig'][1]]
            bstr[mft] = [bion['sig'][0], vv]
        elif mft[0] == 26:
            dd_ = bion['difsig']
            ln_ = len(dd_)
            bstr[mft] = []
            for i in range(ln_):
                vv = [tt * 0.5 for tt in dd_[i][:][2]]
                pass
                bstr[mft].append([dd_[i][0],dd_[i][1], vv])

    pass



def set_ion(zi, bb, elem ='O'):
    nfile = elem + '.pkl'
    cdir = os.path.dirname(__file__)
    fp = os.path.normpath(os.path.join(cdir, "ions_files.zip"))
    if z.is_zipfile(fp):
        fl_ = z.ZipFile(fp,'r')
        print(fl_.printdir())
        try:
            ##            dp = pickle.load(open(nfile))
            sf = fl_.extract(nfile)
            ##            ss_ = sf.split('\n')
            ##            dp = pickle.load(fl_.open(nfile,'r'))
            print(sf)
            o_pkl = open(sf,'rb')
            dp = pickle.load(o_pkl)
            o_pkl.close()
            os.remove(sf)
            fl_.close()
            print('Обрабатывается информация об ионе атома %s. Заряд иона - %d' % (elem, zi))
        except KeyError:
            print('Oтсутствует информация об ионе атома %s' % elem)
            return False

##    dp = {}
##    dp = pickle.load(open( fp))
##    pass

    data_endf(zi, dp, bb)
    pass
    return True

if __name__ == '__main__':
    s = 'N'
    bb = {(23,536):[], (23,537):[]}
    zi = 1
    bi = set_ion(zi, bb, elem=s)
    if bi:
        print((s, list(bb.keys())))
