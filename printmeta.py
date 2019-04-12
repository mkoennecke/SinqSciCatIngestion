#!/usr/bin/python36

"""
  Print meta data for a range of files

  Mark Koennecke, April 2019
"""
import sys
from sinqutils import makeSINQFilename
from instruments import readMetaData,printMeta

if len(sys.argv) < 3:
    print('Usage:\n\tprintmeta.py start stop')
    sys.exit()

inst = 'sans'
year=2018
root='/afs/psi.ch/project/sinqdata/2018/sans'
postfix = 'hdf'



start = int(sys.argv[1])
end = int(sys.argv[2])

for numor in range(start,end):
    dfile = makeSINQFilename(root,year,inst,numor,postfix)
    meta = readMetaData(dfile)
    printMeta(numor,meta)
