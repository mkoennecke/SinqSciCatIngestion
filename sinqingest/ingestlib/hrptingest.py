""""
This module provides the ingestion meta data for HRPT

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
    meta['creationLocation'] = 'HRPT at SINQ'
    meta['dataFormat'] = 'HRPT-NEXUS-HDF5'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta, '/entry1/start_time') 
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/entry1/title')
    temp=getDictItem(scientificmeta,'/entry1/sample/sample_temperature')
    meta['datasetName']=proposal['name']+ "-" + \
                                 getDictItem(scientificmeta,'/entry1/sample/sample_name') \
                                 + "-T=" +temp
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['sample'] = getDictItem(scientificmeta, '/entry1/sample/sample_name')
    meta['sample_temperature'] = getDictItem(scientificmeta, '/entry1/sample/sample_temperature')
    meta['scientificMetadata']=scientificmeta

    # HRPT specific data
    meta['wavelength'] = getDictItem(scientificmeta, '/entry1/HRPT/Monochromator/lambda')
    meta['two_theta'] = getDictItem(scientificmeta, '/entry1/HRPT/HRPT-CERCA-Detector/two_theta_start')
    meta['sample_rotation'] = getDictItem(scientificmeta, '/entry1/sample/sample_table_rotation')
    meta['monitor'] = getDictItem(scientificmeta, '/entry1/HRPT/HRPT-CERCA-Detector/Monitor')
    meta['proton_monitor'] = getDictItem(scientificmeta, 
                                         '/entry1/HRPT/HRPT-CERCA-Detector/proton_monitor')
    meta['radial_collimator_state'] = getDictItem(scientificmeta, 
                                         '/entry1/HRPT/HRPT-CERCA-Detector/radial_collimator_status')
    meta['magnetic_field'] = getDictItem(scientificmeta, '/entry1/sample/magfield')
    meta['sample_changer_position'] = getDictItem(scientificmeta, 
                                                  '/entry1/sample/sample_changer_position')

    return meta
