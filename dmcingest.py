#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py

if len(sys.argv) < 3:
    print('Usage:\n\t:dmcingest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'dmc'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = 'test/dmc'

# ------------- reading Data from DMC files

def readDMC(filename):
    f = h5py.File(filename, 'r')
    meta = {}
    entry = f['entry1']
    meta['title'] = decodeHDF(entry['title'][0])
    meta['collection_description'] = decodeHDF(entry['comment'][0]).strip()
    # todo normalize times to RFC format
    meta['start_time'] = decodeHDF(entry['start_time'][0])
     # todo normalize times to RFC format
    meta['instrument'] = 'DMC'
    meta['wavelength'] = decodeHDF(entry['DMC/Monochromator/lambda'][0])
    meta['detector two_theta start'] = decodeHDF(entry['DMC/DMC-BF3-Detector/two_theta_start'][0])
    meta['proton_monitor'] = decodeHDF(entry['DMC/DMC-BF3-Detector/proton_monitor'][0])
    meta['summed counts'] = decodeHDF(entry['data1/counts'][0])
    sample = {}
    sample['name'] = decodeHDF(entry['sample/sample_name'][0])    
    if pathExists(entry,'sample/sample_changer_position'.split('/')):
        sample['sample_changer position'] = decodeHDF(entry['sample/sample_changer_position'][0])
    else:
        sample['sample_changer position'] = 'UNKNOWN'
    sample['sample rotation'] = decodeHDF(entry['sample/sample_table_rotation'][0])
    if pathExists(entry,'sample/temperature'.split('/')):
        sample['temperature'] = decodeHDF(entry['sample/temperature'][0])
    else:
        sample['temperature'] = 'UNKNOWN'
    if pathExists(entry,'sample/magnet'.split('/')):
        sample['magnet'] = decodeHDF(entry['sample/magnet'][0])
    else:
        sample['magnet'] = 'UNKNOWN'
    meta['sample'] = sample
    meta['user'] = decodeHDF(entry['user/name'][0])
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
        meta['file_time'] = scientificmeta['start_time']
        meta['instrument'] = scientificmeta['instrument']
        meta['owner']=proposal['firstname']+proposal['lastname']
        meta['ownerEmail']=proposal['email']
        meta['title'] = scientificmeta['title']
        meta['sample name'] = scientificmeta['sample']['name']
        if 'temperature' in scientificmeta['sample']:
            tempCandidate=scientificmeta['sample']['temperature']
            if isinstance(tempCandidate, float):
                temp='%.1f' % tempCandidate
        # Magnetfeld? -philip 
        if 'magfield' in scientificmeta['sample']:
            magCandidate = scientificmeta['sample']['magfield']
            if isinstance(magfield, float):
                mag='%.1f' % magCandidate
        # DMC specific
        meta['wavelength'] = scientificmeta['wavelength']
        meta['detector two_theta start'] = scientificmeta['detector two_theta start']
        # sample monitor
        meta['proton_monitor'] = scientificmeta['proton_monitor']
        meta['sample_changer position'] = scientificmeta['sample_changer position']
        meta['sample rotation'] = scientificmeta['sample rotation']
        # check
        meta['summed counts'] = scientificmeta['summed counts']

        meta['principalInvestigator']=proposal['pi_email']
        meta['creationLocation'] = proposal['MeasurementPeriodList'][0]['instrument']
        meta['dataFormat'] = 'DMC-NEXUS-HDF5'
        meta['sourceFolder'] = root
        meta['type']='raw'
        # TODO decide what fields to add to description
        meta['description']=scientificmeta['title']+" / collection:"+scientificmeta['collection_description']
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
sq = SinqFileList(fileroot, int(year), inst, 'hdf', int(start)-1, end)
sqiter = iter(sq)
numor, fname = next(sqiter)
meta = readDMC(fname)
# TODO: get a token
proposal = meta['experiment_identifier']
while fname:
    meta = readDMC(fname)
    printMeta(numor, meta)
    # writeDataset(numor, fname, meta, token)
    numor, fname = next(sqiter)


