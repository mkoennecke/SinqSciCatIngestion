#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py

if len(sys.argv) < 3:
    print('Usage:\n\t:morpheusingest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'morpheus'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = 'test/morpheus'

# ------------- reading Data from MORPHEUS files

def readMORPHEUS(filename):
    f = open(filename, 'r')
    meta = {}
    dataset = ["Date", "User" , "Sample Name", "Title", "ProposalID"]
    x = 0
    for line in f:
        for data in dataset:
            extractedData = line.split('=')
            if (data in extractedData[0] and len(extractedData) > 1):
                meta[extractedData[0]] = extractedData[1]
    meta['instrument'] = 'MORPHEUS'
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
        proposal = {}
        proposal['pi_email'] = scientificmeta['email']
        proposal['name'] = scientificmeta['user']
        proposal['title'] = scientificmeta['proposal_title']
        proposal['proposalID'] = scientificmeta['experiment_identifier']
        proposal['ownerGroup']='a-35433'
        proposal['accessGroups']='a-35433'
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
        if 'temperature' in scientificmeta['sample']:
            tempCandidate=scientificmeta['sample']['temperature']
            if isinstance(tempCandidate, float):
                temp='%.1f' % tempCandidate

        meta['sourceFolder'] = root
        meta['type']='raw'
        # TODO decide what fields to add to description
        temp='undefined'
            
        meta['datasetName']=scientificmeta['user']+"-"+scientificmeta['sample']['name']+"-T="+temp
        meta['ownerGroup']='a-35433'
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
meta = readMORPHEUS(fname)
# TODO: get a token
while fname:
    meta = readMORPHEUS(fname)
    # TODO By commenting away writeDatset() and uncommenting printMeta() you can 
    # do a little test that the reading works OK. 
    printMeta(numor, meta)
    # writeDataset(numo, fname, meta, token)
    numor, fname = next(sqiter)


