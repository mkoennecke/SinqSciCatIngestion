""""
This module provides the ingestion meta data for FOCUS

Mark Koennecke, July 2021
"""
import json
from ingestlib.hdf_reader import hdf5ToDict
from ingestlib.sinqutils import getDictItem

def readIngestionData(filename, scicat, owner, accessGroups):
    try:
        scientificmeta = hdf5ToDict(filename)
    except:
        print('Failed to read %s' % filename)
        return None
    
    # We prefer the proposal data from the database
    proposalID = '20.500.11935/' + getDictItem(scientificmeta, '/entry1/proposal_id').replace(' ', '')
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = getDictItem(scientificmeta, '/entry1/proposal_user/email')
        proposal['name'] = getDictItem(scientificmeta, '/entry1/user/name')
        proposal['title'] = getDictItem(scientificmeta, '/entry1/title')
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']=owner
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'FOCUS at SINQ'
    meta['dataFormat'] = 'FOCUS-NEXUS-HDF5'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta, '/entry1/start_time') 
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/entry1/title')
    temp=getDictItem(scientificmeta,'/entry1/sample/temperature')
    meta['datasetName']=proposal['name']+ "-" + \
                                 getDictItem(scientificmeta,'/entry1/sample/name') \
                                 + "-T=" +temp
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['scientificMetadata']=scientificmeta
    meta['sample'] = getDictItem(scientificmeta, '/entry1/sample/name')
    meta['sample_temperature'] = getDictItem(scientificmeta, '/entry1/sample/temperature')

    # FOCUS special fields
    meta['wavelength'] = getDictItem(scientificmeta, 
                                     '/entry1/FOCUS/monochromator/lambda')
    meta['monitor'] = getDictItem(scientificmeta, 
                                     '/entry1/FOCUS/counter/monitor')
    meta['disk_chopper_speed'] = getDictItem(scientificmeta, 
                                     '/entry1/FOCUS/disk_chopper/rotation_speed')
    meta['fermi_chopper_speed'] = getDictItem(scientificmeta, 
                                     '/entry1/FOCUS/fermi_chopper_speed')

    meta['chopper_phase'] = getDictItem(scientificmeta, 
                                     '/entry1/FOCUS/phase')
    meta['environment'] = getDictItem(scientificmeta, 
                                     '/entry1/sample/environment')

    meta['sample_distance'] = getDictItem(scientificmeta, 
                                     '/entry1/sample/distance')



    return meta
