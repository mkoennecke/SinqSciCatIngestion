#!/usr/bin/python36
"""
   This little program analyses a series of SINQ data files and tries to figure out proposals and 
   data set spans. 

   The start of a new proposal is detected from a change of the experiment_identifier
   in the file metadata.

   In order to test for a chnage of dataset, for all datasets a signature of the meta data is 
   calculated. A change of dataset is detected when the edit distance of the signatures of the 
   current versus the previous file is bigger then a threshold. The edit distance is calculated 
   with the levenshtein algorithm

   Mark Koennecke, April 2019 
"""
from sinqutils import SinqFileList
from instruments import readMetaData,makeSignature
from levenshtein import levenshtein
import pdb

# In the final version get this from the command line parameters or a control file
inst = 'sans'
year=2018
start=1
#end=54677
end=2000
threshold = 10
root='/afs/psi.ch/project/sinqdata/2018/sans'
postfix = 'hdf'

def addFileStuff(meta, root,year,inst,postfix,dfile):
    fileinfo = {}
    fileinfo['root'] = root
    fileinfo['year'] = year
    fileinfo['inst'] = inst
    fileinfo['postfix'] = postfix
    fileinfo['fullpath'] = dfile
    meta['fileinfo'] = fileinfo
    return meta

filelist = SinqFileList(root, year, inst, postfix, start,end)
fliter = iter(filelist)
numor,dfile = fliter.next()
currentmeta = readMetaData(dfile)
currentmeta = addFileStuff(currentmeta,root,year,inst,postfix,dfile)
currentsignature = makeSignature(currentmeta)
currentproposal = currentmeta['experiment_identifier']
print('FD:%s:%d:%s:%s' %(root,year,inst,postfix))
print('PROP:%d:%s ' %(numor,currentmeta['experiment_identifier']))
print('DS:%d:%s ' %(numor,currentsignature))
for numor,dfile in fliter:
    try:
        meta = readMetaData(dfile)
        meta['numor'] = numor
    except Exception as err:
        print('Failed to read %s with %s' %(dfile,str(err)))
    meta = addFileStuff(meta,root,year,inst,postfix,dfile)
    signature = makeSignature(meta)
    if meta['experiment_identifier'] != currentproposal:
        print('PROP:%d:%s ' %(numor,meta['experiment_identifier']))
        currentproposal = meta['experiment_identifier']
        currentsignature = signature
        print('DS:%d:%s ' %(numor,signature))
        continue
    if levenshtein(currentsignature,signature) > threshold:
        print('DS:%d:%s ' % (numor,signature))
        currentsignature = signature
        continue

