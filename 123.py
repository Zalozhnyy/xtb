# import collections
#
# Val = collections.namedtuple('Val', 'capacity flux inductivity')
# print(Val)
# val = Val(capacity=20, flux=30, inductivity=0)
# print(val)
# val._asdict()
#
# print(getattr(val,'capacity'))

import yaml

x = """
electron: True
proton: 
        low_en: 1
        hight_en: 2
pozitron:
        a: 1
        b: 2
"""


files = yaml.load(x)
print(files['proton'])