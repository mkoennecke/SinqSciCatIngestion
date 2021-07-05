"""
  This is a number of utilities for working with SINQ data files. This was developed in 
  the context of the SciCAT indexing project.

  Mark Koennecke, April 2019 
"""
from math import floor
import numpy as np
import math

def makeSINQFilename(root,year,inst,numor,postfix):
    hundreds = floor(numor/1000)
    return '%s/%03d/%s%4dn%06d.%s' % (root,hundreds,inst,year,numor,postfix)

def makeSINQrelFilename(year,inst,numor,postfix):
    hundreds = abs(numor/1000)
    return '%03d/%s%4dn%06d.%s' % (hundreds,inst,year,numor,postfix)


"""
   This class provides an iterator for iterating over SINQ data files. 
"""
class SinqFileList(object):
    def __init__(self,root,year,inst,postfix,start,end):
        self.start = start
        self.end = end
        self.root = root
        self.inst = inst
        self.postfix = postfix
        self.year = year
        self._current = -1

    def __iter__(self):
        self._current = int(self.start)
        return self

    def __next__(self):
        self._current = self._current + 1
        if self._current > int(self.end):
            return self._current, None
        else:
            return self._current, makeSINQFilename(self.root,self.year,self.inst,self._current,self.postfix)


    def next(self):
        return self.__next__()

def metaRecurse(root,meta):
    for key,val in meta.items():
        if isinstance(val,dict):
            newroot = root + '/' + key
            metaRecurse(newroot,val)
        else:
            print(root + '/' + key + '=' + str(val))
    
def printMeta(numor,meta):
    print('################## MetaData for: ' + str(numor))
    metaRecurse('',meta)

def decodeHDF(va):
    """ turn byte strings to normal strings """
    if isinstance(va, bytes):
        try:
            resultValue = va.decode("utf-8")
            pass
        except Exception as e:
            resultValue = va.decode("latin1")
        return resultValue
    elif isinstance(va, np.ndarray):
        # convert byte arrays to string array
        newArray = []
        for a in va:
            if isinstance(a, bytes):
                newArray.append(a.decode("utf-8"))
            else:
                newArray.append(a)
        return newArray
    elif isinstance(va, np.float) and math.isnan(va):
        return None
    else:
        return va.item()

def pathExists(root,path):
    """ Does a path exist in the HDF file? """
    if len(path) == 0:
        return True
    nextobj = path[0]
    if nextobj in root:
        nextroot = root[nextobj]
        newpath = path[1:]
        return pathExists(nextroot,newpath)
    else:
        return False

def recurseDict(dictionary, path):
    if not path:
        return "UNKNOWN"
    key = path[0]
    if key in dictionary:
        obj = dictionary[key]
        if isinstance(obj, dict):
            return recurseDict(obj, path[1:])
        else:
            return str(obj)
    return 'UNKNOWN'

def getDictItem(dictionary, path):
    """
    This is ment to get a data item described by
    path from a HDF5 reading dictionary. If the item
    does not exist, it returns unknown.
    """
    workpath = path.split('/')
    return recurseDict(dictionary, workpath[1:])
