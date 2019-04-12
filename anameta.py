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
from gausssmooth import  smoothListGaussian

if len(sys.argv) < 2:
    print('Usage:\n\anameta.py spanlistfile')
    sys.exit()


numor = []
prop = []
tdiff = []
mdiff = []
elapsed = []
txtdiff = []
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
            mdiff.append(int(ld[3]))
            tdiff.append(float(ld[4])/60)
            elapsed.append(0)
            txtdiff.append(int(ld[5]))
        elif ld[0] == 'ELAPSED':
            elapsed[int(ld[1])-1] = float(ld[2])
        elif ld[0] == 'PROP':
            num = int(ld[1])
            if len(prop) < num+1:
                for i in range(len(prop),num):
                    numor.append(num)
                    prop.append(0)
                    tdiff.append(0)
                    mdiff.append(int(ld[2]))
                    txtdiff.append(0)
                    elapsed.append(0)
            prop[num-1] = 1000
        else:
            pass

#--------------- print it all....

print(' NUMOR PROP   DeltaT  MDIFF TDIFF  ELAPSED')
for n,p,t,m,x,e in zip(numor,prop,tdiff,mdiff,txtdiff,elapsed):
    print('%6d %3d %8.2f   %4d %4d %8.2f' % (n,p,t,m,x,e))

def fixLength(a1,a2):
    diff = len(a1) - len(a2)
    for i in range(diff):
        a2.append(0)
    return a2

# Now let us plot....
n = np.array(numor)
p = np.array(prop)
tds = smoothListGaussian(tdiff)
print(' start %d, after smoothing %d' %(len(tdiff),len(tds)))
t = np.array(fixLength(numor,tds))
m = np.array(mdiff)
stxt = smoothListGaussian(txtdiff)
x = np.array(fixLength(numor,stxt))
e = np.array(elapsed)

print(' n = %d, p = %d, t = %d, m = %d' % (len(numor),len(prop),len(tdiff),len(mdiff)))

plt.plot(n,p,linewidth=4,alpha=0.4)
plt.plot(n,t)
#plt.plot(n,m)
plt.plot(n,x)
#plt.plot(n,e)

plt.legend(['y = Proposal', 'y = time-diff', 'y = meta-diff','y = txt-diff', 'y = elapsed'], loc='upper left')
plt.show()            

