#!/usr/bin/python36
"""
  Little program to generate a plot for a SANS file

  Mark Koennecke, April 2019
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import h5py
import os.path
from matplotlib.colors import ListedColormap

if len(sys.argv) < 2:
    print('Usage:\n\tmake-plot name-of-hdf-file name-of-hdf-file ...')
    sys.exit(1)

rainbow = np.ones((256,4))
rf = open('rainbow.rgb','r')
for i in range(0,256):
    r = int(rf.readline())
    g = int(rf.readline())
    b = int(rf.readline())
    rainbow[i,0] = r/256.0
    rainbow[i,1] = g/256.0
    rainbow[i,2] = b/256.0
rf.close()

rainmap = ListedColormap(rainbow)

for dfile in sys.argv[1:]:
    f5 = h5py.File(dfile,'r')
    ds = f5['entry1/data1/counts']
    plt.imshow(ds,rainmap)
    # plt.show()
    tmp = os.path.basename(dfile)
    fname = tmp + '.png'
    print('Saved image to ' + fname)
    plt.savefig(fname)
    f5.close()


