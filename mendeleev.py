#-*- coding: utf-8 -*-
#!/usr/bin/env python

import os
from tkinter import *
##import PIL as pl

dd = []

def callback(event):
    print(dir(event))
    print("you clicked at", event.x, event.y, event.x_root)
    print(event.char, event.keycode, event.widget)

def elem(k):
    print((' k %d'%k))

def read_elements():
    import csv
    elm = {}
    eln = {}
    with open(os.path.join(os.path.dirname(__file__), 'elements.csv'), "r") as flf:
        rr = csv.DictReader(flf, delimiter='\t')
        for rw in rr:
            elm[rw['El']] = {'NN':int(rw['NN']),'Ro':rw['Ro'], 'A':rw['A']}
            eln[int(rw['NN'])] = {'name':rw['El'],'Ro':rw['Ro'], 'A':rw['A']}

        pass

    return (eln, elm)

def read_elements_x(name):
    with open(name,'rt') as xfl:
        be={}
        xfl.readline()
        for line in xfl:
            t = line.split()
            be[int(t[0])] = [t[1], float(t[2]), float(t[3])]
    sn = {}
    for k in list(be.keys()):
        sn[be[k][0]] = int(k)
    return  (be, sn)



def min0ne(f):
    def tmp(*args, **kwargs):
        res = f(*args, **kwargs)

        return res[0]-1,res[1]-1
    return tmp

@min0ne
def z2rc(Z_):
    """
    """
    endCol_=18

    if Z_==1:
        return(1,1)
    if Z_==2:
        return(1,endCol_)

    if Z_ in (3,4):
        return(2,1+Z_-3)
    if Z_ in range(5,11):
        return(2,8+Z_)

    if Z_ in (11,12):
        return(3,1+Z_-11)
    if Z_ in range(13,19):
        return(3,Z_)

    if Z_ in range(19,37):
        return(4,1+Z_-19)
    if Z_ in range(37,55):
        return(5,1+Z_-37)

    if Z_ in (55,56,57):
        return(6,1+Z_-55)
    if Z_ in range(72,87):
        return(6,4+Z_-72)

    if Z_ in (87,88,89):
        return(7,1+Z_-87)
    if Z_ in range(104,115):
        return(7,4+Z_-104)


    if Z_ in range(58,72):
        return (8,4+Z_-58)
    if Z_ in range(90,104):
        return (9,4+Z_-90)
    return (0,0)


    """   """

def tblMendel( n):

    dmt = read_elements()[0]
    lb = []
    for k in range(1,n):
        i,j=z2rc(k)
        b = Button(root, text=str(k) + ':' + dmt[k]['name'], relief=RIDGE,command=(lambda k=k:elem(k)))
        b.grid(row=i, column=j, sticky=NSEW)
##            b.bind("<Button-1>", callback)
        lb.append(b)


def main():
    """   """
    a = Toplevel()
    tblMendel( 100)
    mainloop()

if __name__ == '__main__':
##    for i in range(1,114):
##        print(z2rc(i))
    root = Tk()
##    gridtable((root))
##    packbox(Toplevel(root))
##    Button(root, text=’Quit’, command=root.quit).pack()
    main()
    mainloop()
    print(dd)
