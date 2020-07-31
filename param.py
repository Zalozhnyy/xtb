# -*- coding: utf-8 -*-
#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        param
# Purpose:
#
# Author:      posev
#
# Created:     02.05.2019
# Copyright:   (c) PC 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import sys
import yaml

golb = """
electron: true
photon: true
mat: mat_files
par: xrb_parameters.ini
"""


def module_path():
    if hasattr(sys, "frozen"):
        return os.path.dirname(
            str(sys.executable, sys.getfilesystemencoding( ))
        )
    return os.path.dirname(os.path.abspath(f'{__file__}'))


def init():
   tt = yaml.load(golb)
   hmd = module_path()
   tt['mat'] = os.path.join(hmd, tt['mat'])
   tt['par'] = os.path.join(hmd, tt['par'])
   tt['home'] = hmd
   # print(tt)

   return tt

if __name__ == '__main__':
    db = {}
    tt = init()
    print(tt)
