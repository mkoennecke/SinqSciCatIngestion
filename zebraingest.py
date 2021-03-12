#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py
from beamInst.scicat import SciCat
from beamInst.ingest_file import main
import json

if len(sys.argv) < 3:
    print('Usage:\n\t:zebraingest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'zebra'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = 'test/zebra'

# ------------- reading Data from ZEBRA files


def readZEBRA(filename):
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
    meta = {}
    if(filename.endswith(cclsuffix) or filename.endswith(datsuffix)):
        f = open(filename, 'r')
        dataset = ["date", "instrument", "user" , "proposal_email", "title", "sample", "temperature", "ProposalID", "stt", "chi", "phi", "om", "nu"]
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
        f = h5py.File(filename, 'r')
        entry = f['entry1']
        meta['title'] = decodeHDF(entry['title'][0])
        meta['collection_description'] = decodeHDF(entry['comment'][0]).strip()
        # todo normalize times to RFC format
        meta['date'] = decodeHDF(entry['start_time'][0])
        # todo normalize times to RFC format
        meta['instrument'] = 'ZEBRA'
        meta['sample'] = decodeHDF(entry['sample/name'][0])
        sample = {}
        if pathExists(entry,'sample/temperature'.split('/')):
            sample['temperature'] = decodeHDF(entry['sample/temperature'][0])
        else:
            sample['temperature'] = 'UNKNOWN'
        if pathExists(entry,'sample/magnet'.split('/')):
            sample['magnet'] = decodeHDF(entry['sample/magnet'][0])
        else:
            sample['magnet'] = 'UNKNOWN'
        meta['sample_directory'] = sample
        meta['user'] = decodeHDF(entry['proposal_user/name'][0])
        meta['proposal_email'] = decodeHDF(entry['proposal_user/email'][0])
        meta['ProposalID'] = decodeHDF(entry['proposal_id'][0])
        # zebra_mode
        meta['detector_mode'] = '2d'
        meta['stt'] = decodeHDF(entry['sample/stt'][0])
        meta['chi'] = decodeHDF(entry['sample/chi'][0])
        meta['phi'] = decodeHDF(entry['sample/phi'][0])
        meta['om'] = decodeHDF(entry['sample/om'][0])
        meta['nu'] = decodeHDF(entry['sample/nu'][0])
        # om, nu
        f.close()
    return meta, filename


def writeDataset(numor, fname,  scientificmeta, username, password):

    # filenameList='intermediate/filelisting-'+str(numor)+'.txt'
    # filelist = open(filenameList,'w') 
    # filelist.write(fname)
    # filelist.close()

    print(scientificmeta)
    proposalId='20.500.11935/'+scientificmeta['ProposalID'].replace(' ','')
    print(proposalId)

    # url='https://dacat-qa.psi.ch/api/v3/Proposals/'+urllib.parse.quote_plus(proposalId)+'?access_token='+token
    # r = requests.get(url)
    # if(r.status_code != 200):
    #     print('Proposal Error Result:',url,r.text)
    #     proposal = {}
    #     proposal['pi_email'] = scientificmeta['email']
    #     proposal['name'] = scientificmeta['user']
    #     proposal['title'] = scientificmeta['proposal_title']
    #     proposal['proposalID'] = scientificmeta['experiment_identifier']
    #     proposal['ownerGroup']='a-35433'
    #     proposal['accessGroups']='a-35433'
    # else:
    #     proposal= json.loads(r.text)

    # create metadata infos from data in proposal and scientific meta data
        # all instruments
    meta = {}
    meta['file_time'] = scientificmeta['date']
    meta['instrument'] = scientificmeta['instrument']
    meta['user']=scientificmeta['user']
    meta['ownerEmail']=scientificmeta['proposal_email']
    meta['title'] = scientificmeta['title']
    if 'temperature' in scientificmeta['sample']:
        tempCandidate=scientificmeta['sample_directory']['temperature']
        if isinstance(tempCandidate, float):
            temp='%.1f' % tempCandidate
    # ZEBRA specific
    meta['detector_mode'] = scientificmeta['detector_mode']
    if 'stt' in scientificmeta:
        meta['stt'] = scientificmeta['stt']
    else:
        meta['stt'] = 'UNKNOWN'
    if 'chi' in scientificmeta:
        meta['chi'] = scientificmeta['chi']
    else:
        meta['chi'] = 'UNKNOWN'
    if 'phi' in scientificmeta:
        meta['phi'] = scientificmeta['phi']
    else:
        meta['phi'] = 'UNKNOWN'
    if 'om' in scientificmeta:
        meta['om'] = scientificmeta['om']
    else:
        meta['om'] = 'UNKNOWN'
    if 'nu' in scientificmeta:
        meta['nu'] = scientificmeta['nu']
    else:
        meta['nu'] = 'UNKNOWN'


    meta['datasetName']=scientificmeta['user']+"-"+scientificmeta['sample']+"-T="
    meta['ownerGroup']='a-35433'
    meta['accessGroups']='a-35433'
    meta['proposalId']=proposalId
    meta['scientificMetadata']=scientificmeta
    # create metadata.json file
    filenameMeta='intermediate/metadata-'+str(year)+'-'+str(start)+'.json'
    metafile = json.dumps(meta, indent=3, sort_keys=True)
    scicat = SciCat("http://localhost:3000")
    with open("beamInst/config.json") as json_file:
        credentials = json.load(json_file)
        scicat.login(credentials["username"], credentials["password"])
    scicat.dataset_post(metafile)
    # run datasetIngestor command
    # subprocess.call(["./datasetIngestor","-testenv", "-ingest", "-allowexistingsource", "-token", token, filenameMeta, filenameList])
        # todo remove files in "intermediate" folder

# ======================== main loop ===========================
sq = SinqFileList(fileroot, int(year), inst, 'hdf', int(start)-1, end)
sqiter = iter(sq)
numor, fname = next(sqiter)
meta, fname = readZEBRA(fname)

# TODO: get a token
while fname:
    meta, fname = readZEBRA(fname)
    # TODO By commenting away writeDatset() and uncommenting printMeta() you can 
    # do a little test that the reading works OK. 
    # printMeta(numor, meta)
    writeDataset(numor, fname, meta, token)
    numor, fname = next(sqiter)

