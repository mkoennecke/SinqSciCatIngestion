#!/usr/bin/python
from sinqutils import SinqFileList
from instruments import readMetaData,makeSignature
from levenshtein import levenshtein
from dateutil import parser

# In the final version get this from the command line parameters
inst = 'sans'
year=2018
start=1
end=54677
#end=2000
threshold = 10
root='/afs/psi.ch/project/sinqdata/2018/sans'
postfix = 'hdf'


filelist = SinqFileList(root, year, inst, postfix, start,end)
fliter = iter(filelist)
numor,dfile = fliter.next()
currentmeta = readMetaData(dfile)
currentsignature = makeSignature(currentmeta)
currentproposal = currentmeta['experiment_identifier']
print('FD:%s:%d:%s:%s' %(root,year,inst,postfix))
print('PROP:%d:%d:%s ' %(numor,0,currentmeta['experiment_identifier']))
print('DS:%d:%d:%s ' %(numor,0,currentsignature))
previousmeta = currentmeta
tdiffsig = currentsignature
for numor,dfile in fliter:
    try:
        meta = readMetaData(dfile)
        meta['numor'] = numor
    except Exception as err:
        print('Failed to read %s with %s' %(dfile,str(err)))
    signature = makeSignature(meta)
    etime = parser.parse(previousmeta['end_time'])
    stime = parser.parse(meta['start_time'])
    diff = (stime-etime).seconds
    if(diff > 4000):
        print('PREDICT:%d' % (numor))
    print('TDIFF:%d:%d:%d:%f' %(numor-1,numor,levenshtein(tdiffsig,signature),diff))
    etime = parser.parse(meta['end_time'])
    print('ELAPSED:%d:%f' % (numor,(stime-etime).seconds))
    previousmeta = meta
    tdiffsig = signature
    mdiff = levenshtein(currentsignature,signature)
    if meta['experiment_identifier'] != currentproposal:
        print('PROP:%d:%d:%s ' %(numor,mdiff,meta['experiment_identifier']))
        currentproposal = meta['experiment_identifier']
        currentsignature = signature
        print('DS:%d:%d:%s ' %(numor,mdiff,signature))
        continue
    if levenshtein(currentsignature,signature) > threshold:
        print('DS:%d:%d:%s ' % (numor,levenshtein(currentsignature,signature),signature))
        currentsignature = signature
        continue

