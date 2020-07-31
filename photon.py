#!/usr/bin/env python
# -*- coding: utf-8 -*-

## @package Program
# Модуль для построения энергетических и угловых распределений
# фотонов и электронов при их взаимодействии с веществом
#-------------------------------------------------------------------------------
import xtb_photon as xph

def main(dp):
    print((dp['xI']))
    print((dp['Mt']))
    xph.main(dp['xI'],  dp['Mt'], dp['mf'], dp['path'])

if __name__ == '__main__':
    main()
