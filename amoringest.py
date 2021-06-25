#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py

if len(sys.argv) < 3:
    print('Usage:\n\t:amoringest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'amor'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = 'test/amor'

# ------------- reading Data from AMOR files


def readAMOR(filename):
    if os.path.exists(filename):
        print('hdf file found')
    else:
        filename = filename.replace(".hdf", ".ccl")
        if os.path.exists(filename):
            print('ccl file found')
        else:
            filename = filename.replace(".ccl", ".dat")
            if os.path.exists(filename):
                print('dat file found')
            else:
                print('datatype unknown')
    cclsuffix = '.ccl'
    datsuffix = '.dat'
    hdfsuffix = '.hdf'
    print(filename)
    meta = {}
    dataset = ["Date", "User" , "Sample Name", "Title", "ProposalID"]
    if(filename.endswith(cclsuffix) or filename.endswith(datsuffix)):
        f = open(filename, 'r')
        x = 0
        for line in f:
            if line.startswith('#data'):
                break
            extractedData = line.split('=')
            if len(extractedData) == 2:
                key = extractedData[0].strip()
                if key in dataset:
                    meta[key] = extractedData[1].strip()
        meta['detector_mode'] = '1d'        
        f.close()

    elif(filename.endswith(hdfsuffix)):
        print('read data')
        f = h5py.File(filename, 'r')
        entry = f['entry1']
        meta['title'] = decodeHDF(entry['title'][0])
        meta['collection_description'] = decodeHDF(entry['comment'][0]).strip()
        # todo normalize times to RFC format
        meta['date'] = decodeHDF(entry['start_time'][0])
        # todo normalize times to RFC format
        meta['instrument'] = 'AMOR'
        sample = {}
        sample['name'] = decodeHDF(entry['sample/name'][0])
        if pathExists(entry,'sample/temperature'.split('/')):
            sample['temperature'] = decodeHDF(entry['sample/temperature'][0])
        else:
            sample['temperature'] = 'UNKNOWN'
        if pathExists(entry,'sample/magnet'.split('/')):
            sample['magnet'] = decodeHDF(entry['sample/magnet'][0])
        else:
            sample['magnet'] = 'UNKNOWN'
        meta['sample'] = sample
        meta['user'] = decodeHDF(entry['proposal_user/name'][0])
        meta['email'] = decodeHDF(entry['proposal_user/email'][0])
        meta['experiment_identifier'] = decodeHDF(entry['proposal_id'][0])
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
        meta['file_time'] = scientificmeta['date']
        meta['instrument'] = scientificmeta['instrument']
        meta['user']=scientificmeta['user']
        meta['ownerEmail']=proposal['proposal_email']
        meta['title'] = scientificmeta['title']
        if 'temperature' in scientificmeta['sample']:
            tempCandidate=scientificmeta['sample']['temperature']
            if isinstance(tempCandidate, float):
                temp='%.1f' % tempCandidate



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
sq = SinqFileList(fileroot, int(year), inst, 'hdf', int(start)-1, end)
sqiter = iter(sq)
numor, fname = next(sqiter)
meta, fname = readAMOR(fname)
# TODO: get a token
while fname:
    meta, fname = readAMOR(fname)
    # TODO By commenting away writeDatset() and uncommenting printMeta() you can 
    # do a little test that the reading works OK. 
    printMeta(numor, meta)
    # writeDataset(numo, fname, meta, token)
    numor, fname = next(sqiter)
