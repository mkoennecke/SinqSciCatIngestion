#!/usr/bin/python36
"""
  This is the actual ingestor for SciCat and SINQ data files


  Mark Koennecke, April 2019
"""

import sys
from SciCat import SciCat
from sinqutils import makeSINQFilename
from instruments import readMetaData

if len(sys.argv) < 2:
    print('Usage:\n\tscingest.py spanlistfile')
    sys.exit()


scicat = SciCat()

def loadMeta(numor):
    fname = makeSINQFilename(root,int(year),inst,int(numor),postfix)
    meta = readMetaData(fname.strip())
    return meta

with open(sys.argv[1],'r') as fin:
    for line in fin:
        ld = line.split(':')
        if ld[0] == 'FD':
            root = ld[1]
            year = ld[2]
            inst = ld[3]
            postfix = ld[4]
        elif ld[0] == 'PROP':
            numor = int(ld[1])
            dsstart = numor
            meta = loadMeta(numor)
            scicat.writeProposal(meta)
        elif ld[0] == 'DS':
            numor = int(ld[1])
            meta = loadMeta(numor-1)
            scicat.writeDataset(dsstart,numor-1,meta)
            dsstart = numor
        else:
            print('Unrecoginzed input ' + line)


            
