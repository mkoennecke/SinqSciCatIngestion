#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py

if len(sys.argv) < 3:
    print('Usage:\n\t:narzissingest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'narziss'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = 'test/narziss'

# ------------- reading Data from NARZISS files

def readNARZISS(filename):
    f = open(filename, 'r')
    meta = {}
    dataset = ["Date", "User" , "Sample Name", "Title", "ProposalID"]
    x = 0
    for line in f:
        for data in dataset:
            extractedData = line.split('=')
            if (data in extractedData[0] and len(extractedData) > 1):
                meta[extractedData[0]] = extractedData[1]
    meta['instrument'] = 'NARZISS'
    f.close()
    return meta

def writeDataset(numor, fname,  scientificmeta, token):

    filenameList='intermediate/filelisting-'+str(numor)+'.txt'
    filelist = open(filenameList,'w') 
    filelist.write(fname)
    filelist.close()

    # print(scientificmeta)
    proposalId='20.500.11935/'+scientificmeta['experiment_identifier'].replace(' ','')
    print(proposalId)

    url='https://dacat-qa.psi.ch/api/v3/Proposals/'+urllib.parse.quote_plus(proposalId)+'?access_token='+token
    r = requests.get(url)
    if(r.status_code != 200):
        print('Proposal Error Result:',url,r.text)
    else:
        proposal= json.loads(r.text)

    # create metadata infos from data in proposal and scientific meta data
        # all instruments
        meta = {}
        meta['file_time'] = scientificmeta['Date']
        meta['instrument'] = scientificmeta['Instrument']
        meta['user']= scientificmeta['User']
        meta['title'] = scientificmeta['Title']
        meta['sample name'] = scientificmeta['Sample Name']
        meta['sourceFolder'] = root
        meta['type']='raw'
        # TODO decide what fields to add to description
        temp='undefined'
            
        meta['datasetName']=scientificmeta['user']+"-"+scientificmeta['sample']['name']+"-T="+temp
        meta['ownerGroup']=proposal['ownerGroup']
        meta['accessGroups']=proposal['accessGroups']
        meta['proposalId']=proposalId
        meta['scientificMetadata']=scientificmeta
        # create metadata.json file
        filenameMeta='intermediate/metadata-'+str(year)+'-'+str(start)+'.json'
        metafile = open(filenameMeta,'w') 
        metafile.write(json.dumps(meta, indent=3, sort_keys=True))
        metafile.close()
        # run datasetIngestor command
        subprocess.call(["./datasetIngestor","-testenv", "-ingest", "-allowexistingsource", "-token", token, filenameMeta, filenameList])
            # todo remove files in "intermediate" folder


# ======================== main loop ===========================
sq = SinqFileList(fileroot, int(year), inst, 'dat', int(start)-1, end)
sqiter = iter(sq)
numor, fname = next(sqiter)
meta = readNARZISS(fname)
# TODO: get a token
while fname:
    meta = readNARZISS(fname)
    # TODO By commenting away writeDatset() and uncommenting printMeta() you can 
    # do a little test that the reading works OK. 
    printMeta(numor, meta)
    # writeDataset(numo, fname, meta, token)
    numor, fname = next(sqiter)


