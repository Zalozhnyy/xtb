# -*- coding: utf-8 -*-
#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        cfg
# Purpose:
#
# Author:      PC
#
# Created:     30.01.2019
# Copyright:   (c) PC 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import collections

Val = collections.namedtuple('Val','dirmat extmat nrmat nrlay')

val = Val(
        extmat = 'mrat',
        dirmat = 'mat_files',
        nrmat = 15,
        nrlay = 20
        )

##val = {'ext': 'mrat',
##       'dir': 'mat_files',
##       'nrowmat': 15,
##       'nrowlay': 20, }


##def main():
##    pass

if __name__ == '__main__':
    print(val)
    pass
##    main()
