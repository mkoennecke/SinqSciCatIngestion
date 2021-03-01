#!/usr/bin/python36
"""
  This is the actual ingestor for SciCat and SINQ data files


  Mark Koennecke, April 2019
"""

import sys
from SciCat import SciCat
from sinqutils import makeSINQFilename
from instruments import readMetaData

if len(sys.argv) < 3:
    print('Usage:\n\tscingest.py span-results.txt token')
    print('Please note: the datasetIngestor command must be in the PATH. The token should be the token generated for  e.g. sinqsans-i user')
    sys.exit()


scicat = SciCat()

token = sys.argv[2]

def loadMeta(numor):
    fname = makeSINQFilename(root,int(year),inst,int(numor),postfix)
    meta = readMetaData(fname.strip())
    return meta

nextds = False
with open(sys.argv[1],'r') as fin:
    for line in fin:
        ld = line.split(':')
        if ld[0] == 'FD':
            root = ld[1]
            year = ld[2]
            inst = ld[3]
            postfix = ld[4].strip()
        elif ld[0] == 'PROP':
            numor = int(ld[1])
            dsstart = numor
            meta = loadMeta(numor)
            scicat.writeProposal(meta)
        elif ld[0] == 'DS':
            numor = int(ld[1])
            meta = loadMeta(numor-1)
            if nextds: 
                attachmentFile=scicat.createAttachmentFile(root, year, inst, postfix, dsstart)
                scicat.writeDataset(root, year, inst, postfix, dsstart, numor-1, meta, token,attachmentFile)
            nextds = True
            dsstart = numor
        else:
            print('Unrecognized input ' + line)

