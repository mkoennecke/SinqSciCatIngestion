#!/usr/bin/python
"""
  This actually plots the meta differences in order to 
  determine if we can properly predict proposal boundaries 
  from raw meta data, without explicit experiment_identifier, only. 
  This requires a file as created by the companion program 
  tdiff-detector as input


  Mark Koennecke, April 2019
"""

import sys
import matplotlib.pyplot as plt
import numpy as np

if len(sys.argv) < 2:
    print('Usage:\n\anameta.py spanlistfile')
    sys.exit()


numor = []
prop = []
tdiff = []
mdiff = []

with open(sys.argv[1],'r') as fin:
    for line in fin:
        ld = line.split(':')
        if ld[0] == 'FD':
            root = ld[1]
            year = ld[2]
            inst = ld[3]
            postfix = ld[4]
        elif ld[0] == 'TDIFF':
            numor.append(int(ld[1]))
            prop.append(0)
            mdiff.append(int(ld[3])*10)
            tdiff.append(float(ld[4])/60)
        elif ld[0] == 'PROP':
            num = int(ld[1])
            if len(prop) < num+1:
                for i in range(len(prop),num):
                    numor.append(num)
                    prop.append(0)
                    tdiff.append(0)
                    mdiff.append(0)
            prop[num-1] = 1000
        else:
            pass

#--------------- print it all....

print(' NUMOR PROP   DeltaT  MDIFF')
for n,p,t,m in zip(numor,prop,tdiff,mdiff):
    print('%6d %3d %8.2f   %4d' % (n,p,t,m))


# Now let us plot....
n = np.array(numor)
p = np.array(prop)
t = np.array(tdiff)
m = np.array(mdiff)

print(' n = %d, p = %d, t = %d, m = %d' % (len(numor),len(prop),len(tdiff),len(mdiff)))

plt.plot(n,p,linewidth=10)
plt.plot(n,t)
plt.plot(n,m)

plt.legend(['y = Proposal', 'y = time-diff', 'y = meta-diff'], loc='upper left')
plt.show()            

