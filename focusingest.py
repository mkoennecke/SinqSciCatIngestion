#!/usr/bin/env python3
import sys
import os
from sinqutils import SinqFileList, decodeHDF, pathExists, printMeta
import h5py

if len(sys.argv) < 3:
    print('Usage:\n\t:focusingest.py year start end')
    sys.exit(1)

# ================== Configuration

inst = 'focus'
year = sys.argv[1]
start = sys.argv[2]
end = sys.argv[3]

fileroot = 'test/focus'

# ------------- reading Data from FOCUS files

def readFOCUS(filename):
    f = h5py.File(filename, 'r')
    meta = {}
    entry = f['entry1']
    meta['title'] = decodeHDF(entry['title'][0])
    meta['collection_description'] = decodeHDF(entry['comment'][0]).strip()
    # todo normalize times to RFC format
    meta['start_time'] = decodeHDF(entry['start_time'][0])
     # todo normalize times to RFC format
    meta['end_time'] = decodeHDF(entry['end_time'][0])
    meta['instrument'] = 'FOCUS'

    meta['wavelength'] = decodeHDF(entry['FOCUS/monochromator/lambda'][0])
    if pathExists(entry,'focus2d'):
        meta['2ddetector'] = 'yes'
    else:
        meta['2ddetector'] = 'no'
    sample = {}
    sample['name'] = decodeHDF(entry['sample/name'][0])
    sample['environment'] = decodeHDF(entry['sample/environment'][0])
    sample['distance'] = decodeHDF(entry['sample/distance'][0])
    if pathExists(entry,'sample/temperature'.split('/')):
        sample['temperature'] = decodeHDF(entry['sample/temperature'][0])
    else:
        sample['temperature'] = 'UNKNOWN'
    # TODO: check a number of files and see if you can find an entry for magnets.
    # It coulkd also be that the name is magnetic_field.    
    if pathExists(entry,'sample/magnet'.split('/')):
        sample['magnet'] = decodeHDF(entry['sample/magnet'][0])
    else:
        sample['magnet'] = 'UNKNOWN'
    meta['sample'] = sample
    # TODO
    meta['monitor'] = 27.
    meta['user'] = decodeHDF(entry['user/name'][0])
    meta['email'] = decodeHDF(entry['user/email'][0])
    meta['experiment_identifier'] = decodeHDF(entry['proposal_id'][0])
    meta['disk_chopper_speed'] = decodeHDF(entry['FOCUS/disk_chopper/rotation_speed'])
    meta['fermi_chopper_speed'] = decodeHDF(entry['FOCUS/fermi_chopper/rotation_speed'])
    # TODO: ratio und phase
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
        meta['file_time'] = "start time:"+scientificmeta['start_time']+"end time:"+scientificmeta['end_time']
        meta['instrument'] = scientificmeta['instrument']
        meta['owner']=proposal['firstname']+ ' ' + proposal['lastname']
        meta['ownerEmail']=proposal['email']
        meta['title'] = scientificmeta['title']
        meta['sample name'] = scientificmeta['sample']['name']
        if 'temperature' in scientificmeta['sample']:
            tempCandidate=scientificmeta['sample']['temperature']
            if isinstance(tempCandidate, float):
                temp='%.1f' % tempCandidate
        # FOCUS specific
        meta['environment'] = scientificmeta['sample']['environment']
        # check data for wavelength and chopper_speeds -philip
        meta['wavelength'] = scientificmeta['wavelength']
        meta['chopper_speeds'] = "disk chopper rotation speed:"+scientificmeta['disk_chopper_speed']+"fermi chopper rotation speed:"+scientificmeta['fermi_chopper_speed']
        meta['sample_distance'] = scientificmeta['sample']['distance']
        # TODO
        meta['focus2d_counts'] = scientificmeta['focus2d_counts']
        meta['focus2d_time_binning'] = scientificmeta['focus2d_time_binning']
        # Comment from Mark: the 2D flag belongs into the scientific metadata. The flag can be derived from checking for the 
        # existence of a focus2d group at entry level. 

        meta['principalInvestigator']=proposal['pi_email']
        meta['creationLocation'] = proposal['MeasurementPeriodList'][0]['instrument']
        meta['dataFormat'] = 'FOCUS-NEXUS-HDF5'
        meta['sourceFolder'] = root
        meta['type']='raw'
        # TODO decide what fields to add to description
        meta['description']=scientificmeta['title']+" / collection:"+scientificmeta['collection_description']
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
sq = SinqFileList(fileroot, int(year), inst, 'hdf', start, end)
sqiter = iter(sq)
numor, fname = next(sqiter)
meta = readFOCUS(fname)
# TODO: get a token
proposal = meta['experiment_identifier']
while fname:
    meta = readFOCUS(fname)
    # TODO By commenting away writeDatset() and uncommenting printMeta() you can 
    # do a little test that the reading works OK. 
    printMeta(numor, meta)
    # writeDataset(numo, fname, meta, token)
    numor, fname = next(sqiter)


