"""
This module reads a HDF5 file and converts it into a
python dictionary. Optionally, bulk data is suppressed, 
such that only the meta data is read

Mark Koennecke, July 2021
"""

import h5py
from h5py._hl.group import Group
from h5py._hl.dataset import Dataset
import numpy as np
import math

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

def recurseGroup(group, suppress_data):
    result = {}
    for it in group.keys():
        obj = group[it]
        if isinstance(obj, Group):
            result[it] = recurseGroup(obj, suppress_data)
        elif isinstance(obj, Dataset):
            if obj.size > 10 and suppress_data:
                pass
            else:
                result[it] = decodeHDF(obj[0])
    return result


def hdf5ToDict(filename, suppress_data=True):
    hdf = h5py.File(filename, 'r')
    result = recurseGroup(hdf, suppress_data)
    hdf.close()
    return result

    
