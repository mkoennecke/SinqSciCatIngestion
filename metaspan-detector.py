#!/usr/bin/python36
"""
   This little program analyses a series of SINQ data files and tries to figure out proposals and 
   data set spans. 

   The start of a new proposal is detected from a change of the experiment_identifier
   in the file metadata.

   This is a second version which tracks complete differences between files. If there is a big change,
   like  many fields changing or very big differences, then a new dataset is assumed. Or, when the 
   proposal_id or the user changes, it is a proposal change. 

   Mark Koennecke, April 2019 
"""
from sinqutils import SinqFileList
from instruments import readMetaData,makeSignature
from levenshtein import levenshtein
import h5py
import numpy as np
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
            return diff
        else:
            return None
    else:
        None

def compareDataset(in1, in2, path):
    d1 = in1.get(path)
    d2 = in2.get(path)
    if toIgnore(d1):
#        print('Ignoring ' + path)
        return None
    if d2 is None:
        print('Second misses path: ' +path)
        return 'Missing'
    diff = testSpecial(d1,d2,path)
    if diff != None:
        return diff
    if  d1.dtype.type is np.string_:
        if d1[0] != d2[0]:
            return levenshtein(d1[0],d2[0])
        else:
            return None
    elif d1.dtype.kind ==  'f':
        diff = abs((d1[0] - d2[0]))
        if diff > .1:
            return diff
        else:
            return None
    else:
#       print('Integer DS: ' + path)
        diff =  abs(d1[0] - d2[0])
        if diff > 0:
            return diff
        else:
            return None


def metaCompare(firstfile,secondfile):
    f1 = h5py.File(firstfile,'r')
    f2 = h5py.File(secondfile,'r')
    
    dsList = []
    def func(name,obj):
        if isinstance(obj,h5py.Dataset):
            dsList.append(name)
    f1.visititems(func)

    diffs = {}
    for dsName in dsList:
        diffval = compareDataset(f1,f2,dsName)
        if diffval != None:
            diffs[dsName] = diffval

    f1.close()
    f2.close()
    return diffs

def isDiffSignificant(previous_diff,current_diff):
    significant_fields = {'entry1/sample/magnetic_field': 10.,'entry1/sample/temperature':10.,}
    if previous_diff == None:
        # Just started: cannot say
        return False
    if len(current_diff) < 1:
        # Little change
        return False
    if isProposalChange(current_diff):
        return True
    if 'entry1/sample/name' in current_diff:
        return True
    if abs(len(previous_diff) - len(current_diff)) >= 2:
        # A lot changed
        return True
    # Now compare the size of the differences against each other
    for key,val in current_diff.items():
        if key in previous_diff:
            if abs(val-previous_diff[key]) > 2*val:
                return True
        else:
            if key in significant_fields and val > significant_fields[key]:
                return True
    # Only incremental changes found
    return False
    
def isProposalChange(diff):
    if '/entry1/proposal_id' in diff or '/entry1/user/name' in diff:
        return True
    else:
        return False

filelist = SinqFileList(root, year, inst, postfix, start,end)
fliter = iter(filelist)
numor,dfile = fliter.next()
currentmeta = readMetaData(dfile)
currentmeta = addFileStuff(currentmeta,root,year,inst,postfix,dfile)
currentproposal = currentmeta['experiment_identifier']
print('FD:%s:%d:%s:%s' %(root,year,inst,postfix))
print('PROP:%d:%s ' %(numor,currentmeta['experiment_identifier']))
print('DS:%d ' %(numor))
previous_diff = None
previous_file = dfile
for numor,dfile in fliter:
    if numor == 80:
        pdb.set_trace()
    diff = metaCompare(previous_file,dfile)
    if isDiffSignificant(previous_diff,diff):
        if isProposalChange(diff):
            currentmeta = readMetaData(dfile)
            currentMeta = addFileStuff(currentmeta,root,year,inst,postfix,dfile)
            print('PROP:%d:%s ' %(numor,currentmeta['experiment_identifier']))
        print('DS:%d' %(numor))
        previous_diff = None
    else:
        previous_diff = diff
    previous_file = dfile
