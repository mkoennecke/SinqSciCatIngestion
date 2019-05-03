#!/usr/bin/python
"""
  A little program which prints the meta data differences between files.
  For research about how meta data changes.

  Mark Koennecke, April 2019
"""
import sys
from sinqutils import SinqFileList
import h5py
import numpy as np
import pdb

if len(sys.argv) < 3:
    print('Usage:\n\meta-diff.py start stop')
    sys.exit(1)

start = int(sys.argv[1])
end = int(sys.argv[2])
inst = 'sans'
year=2018
root='/afs/psi.ch/project/sinqdata/2018/sans'
postfix = 'hdf'

def toIgnore(ds):
    ignoreList = ['start_time', 'end_time', 'counts', 'counting_time', 'preset', 'detector/temperature',\
                  'data','beam_center_x','beam_center_y']
    for name in ignoreList:
        if ds.name.find(name) >= 0:
            return True
    if ds.len() > 1:
        return True
    return False

# returns True when handled, False else
def testSpecial(d1,d2,name):
    if name.find('rotation_speed') >= 0:
        diff = abs(d1[0]-d2[0])
        if diff > 20:
            print(name + ' differs ' + str(d1[0]) + ' versus ' + str(d2[0]))
            return True
        else:
            return False
    else:
        False

def compareDataset(in1, in2, path):
    d1 = in1.get(path)
    d2 = in2.get(path)
    if toIgnore(d1):
#        print('Ignoring ' + path)
        return False
    if d2 is None:
        print('Second misses path: ' +path)
        return True
    test = testSpecial(d1,d2,path)
    if test:
        return True
    if  d1.dtype.type is np.string_:
        if d1[0] != d2[0]:
            print(path + ' differs ' + d1[0] + ' versus ' + d2[0])
            return True
        else:
            return False
    elif d1.dtype.kind ==  'f':
        diff = abs((d1[0] - d2[0]))
        if diff > .1:
            print(path + ' differs ' + str(d1[0]) + ' versus ' + str(d2[0]))
            return True
        else:
            return False
    else:
#       print('Integer DS: ' + path)
        diff =  abs(d1[0] - d2[0])
        if diff > 0:
            print(path + ' differs ' + str(d1[0]) + ' versus ' + str(d2[0]))
            return True
        else:
            return False



def metaCompare(firstfile,secondfile):
    count = 0
    f1 = h5py.File(firstfile,'r')
    f2 = h5py.File(secondfile,'r')
    
    dsList = []
    def func(name,obj):
        if isinstance(obj,h5py.Dataset):
            dsList.append(name)
    f1.visititems(func)

    for dsName in dsList:
        test = compareDataset(f1,f2,dsName)
        if test:
            count = count + 1

    f1.close()
    f2.close()
    return count

filelist = SinqFileList(root, year, inst, postfix, start,end)
fliter = iter(filelist)
numor1,firstfile = fliter.next()
for numor,dfile in fliter:
    print('####################################### %d versus %d' %(numor1,numor))
#    if numor == 3:
#        pdb.set_trace()
    count = metaCompare(firstfile,dfile)
    print('==== COUNT: %d' %(count))
    firstfile = dfile
    numor1 = numor



