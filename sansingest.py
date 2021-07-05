#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py
from beamInst.scicat import SciCat
import pdb
import urllib
import requests
from pathlib import Path
import time

if len(sys.argv) < 3:
    print('Usage:\n\t:sansingest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'sans'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = '/afs/psi.ch/project/sinqdata/2021/sans'

# ------------- reading Data from SANS files

def readSANS(filename):
    f = h5py.File(filename, 'r')
    meta = {}
    entry = f['entry1']
    meta['title'] = decodeHDF(entry['title'][0])
    #meta['collection_description'] = decodeHDF(entry['comment'][0]).strip()
    # todo normalize times to RFC format
    meta['start_time'] = decodeHDF(entry['start_time'][0])
     # todo normalize times to RFC format
    meta['end_time'] = decodeHDF(entry['end_time'][0])
    meta['instrument'] = 'SANS'
    source = {}
    source['type'] = 'Spallation Neutron Source'
    source['probe'] = 'neutron'
    source['name'] = 'SINQ at PSI'
    meta['source'] = source
    meta['wavelength'] = decodeHDF(entry['SANS/Dornier-VS/lambda'][0])
    coll = {}
    coll['shape'] = 'nxcylinder'
    coll['size'] = decodeHDF(entry['SANS/collimator/length'][0])
    meta['collimator'] = coll
    detector = {}
    # todo find proper transformation detector['sum'] = np.sum(decodeHDF(entry['SANS/detector/counts']))
    detector['distance'] = decodeHDF(entry['SANS/detector/x_position'][0])
    detector['polar_angle'] = 0.
    detector['azimuthal_angle'] = 0.
    detector['aequatorial_angle'] = 0.
    detector['x_pixel_size'] = 7.5
    detector['y_pixel_size'] = 7.5
    if pathExists(entry,'SANS/detector/beam_center_x'.split('/')):
        detector['beam_center_x'] = decodeHDF(entry['SANS/detector/beam_center_x'][0])*7.5
        detector['beam_center_y'] = decodeHDF(entry['SANS/detector/beam_center_y'][0])*7.5
    meta['detector'] = detector
    sample = {}
    sample['name'] = decodeHDF(entry['sample/name'][0])
    #sample['environment'] = decodeHDF(entry['sample/environment'][0])
    sample['aequatorial_angle'] = 0.
    if pathExists(entry,'sample/temperature'.split('/')):
        sample['temperature'] = decodeHDF(entry['sample/temperature'][0])
    else:
        sample['temperature'] = 'UNKNOWN'
    if pathExists(entry,'sample/magnet'.split('/')):
        sample['magnet'] = decodeHDF(entry['sample/magnet'][0])
    else:
        sample['magnet'] = 'UNKNOWN'
    meta['sample'] = sample
    control = {}
    control['mode'] = decodeHDF(entry['SANS/detector/count_mode'][0])
    control['preset'] = decodeHDF(entry['SANS/detector/preset'][0])
    control['time'] = decodeHDF(entry['SANS/detector/counting_time'][0])
    control['integral'] = decodeHDF(entry['SANS/monitor1/counts'][0])
    control['monitor2'] = decodeHDF(entry['SANS/monitor2/counts'][0])
    control['monitor3'] = decodeHDF(entry['SANS/monitor3/counts'][0])
    meta['control'] = control
    meta['user'] = decodeHDF(entry['user/name'][0])
    if pathExists(entry, 'proposal_user/email'.split('/')):
        meta['email'] = decodeHDF(entry['proposal_user/email'][0])
    else:
        meta['email'] = 'joachim.kohlbrecher@psi.ch'
    meta['proposal_title'] = decodeHDF(entry['proposal_title'][0])
    meta['experiment_identifier'] = decodeHDF(entry['proposal_id'][0])
    # todo: commented because not existing: meta['attenuator'] = decodeHDF(entry['SANS/attenuator/selection'][0])
    f.close()
    return meta

def makeFileEntry(fname):
    entry = {}
    # Get to the real file, we are looking at symlinks here
    p = Path(fname).resolve()
    stat = p.stat()
    entry['path'] = str(p)
    entry['size'] = stat.st_size
    entry['gid'] = stat.st_gid
    entry['uid'] = stat.st_uid
    tt = time.localtime(stat.st_ctime)
    entry['time'] = time.strftime('%Y-%m-%dT%H:%M:%S', tt)
    entry['perm'] = oct(stat.st_mode)[-3:]
    return entry

def prepareDataset(numor, fname,  scientificmeta, token):

    # print(scientificmeta)
    proposalId='20.500.11935/'+scientificmeta['experiment_identifier'].replace(' ','')
    #print(proposalId)

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
        proposal['accessGroups']=['a-35433',]
    else:
        proposal= json.loads(r.text)

    # create metadata infos from data in proposal and scientific meta data

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'SANS at SINQ'
    meta['dataFormat'] = 'SANS-NEXUS-HDF5'
    meta['sourceFolder'] = fileroot
    meta['owner']=scientificmeta['user']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = scientificmeta['start_time'] 
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    # TODO decide what fields to add to description
    meta['description']=scientificmeta['title']
    temp='undefined'
    if 'temperature' in scientificmeta['sample']:
        tempCandidate=scientificmeta['sample']['temperature']
        if isinstance(tempCandidate, float):
            temp='%.1f' % tempCandidate
            
    meta['datasetName']=scientificmeta['user']+"-"+scientificmeta['sample']['name']+"-T="+temp
    meta['ownerGroup']='a-35433'
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalId
    meta['scientificMetadata']=scientificmeta
        
    datablock = {}
    datablock['size'] = 1
    datablock['dataFileList'] = [makeFileEntry(fname),]
    datablock['datasetId']='Undefined'
    return meta, datablock

# ======================== main loop ===========================
sq = SinqFileList(fileroot, int(year), inst, 'hdf', int(start)-1, end)
#pdb.set_trace()
sqiter = iter(sq)
numor, fname = next(sqiter)
meta = readSANS(fname)
sc = SciCat('https://dacat-qa.psi.ch')
token = sc.loginPSI('koennecke', '21:ErikaPSI')
proposal = meta['experiment_identifier']
while fname:
    meta = readSANS(fname)
    #printMeta(numor, meta)
    meta, datablock = prepareDataset(numor, fname, meta, token)
    res = sc.dataset_post(meta)
    stat = sc.origdatablock_post(res['pid'], datablock)
    numor, fname = next(sqiter)


