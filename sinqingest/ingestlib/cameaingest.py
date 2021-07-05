""""
This module provides the ingestion meta data for CAMELA

Mark Koennecke, July 2021
"""
import json
from ingestlib.ingestlib.hdf_reader import hdf5ToDict
from ingestlib.ingestlib.sinqutils import getDictItem

def readIngestionData(filename, scicat, owner, accessGroups):
    try:
        scientificmeta = hdf5ToDict(filename)
    except:
        print('Failed to read %s' % filename)
        return None

    # Clean some stuff out which cannot be easily processed by json
    sample = scientificmeta['entry']['sample']
    del sample['orientation_matrix']
    del sample['plane_normal']
    del sample['plane_vector_1']
    del sample['plane_vector_2']

    # We prefer the proposal data from the database
    proposalID = '20.500.11935/' + getDictItem(scientificmeta, '/entry/proposal_id').replace(' ', '')
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = getDictItem(scientificmeta, '/entry/proposal_user/email')
        proposal['name'] = getDictItem(scientificmeta, '/entry/user/name')
        proposal['title'] = getDictItem(scientificmeta, '/entry/title')
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']=owner
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'CAMEA at SINQ'
    meta['dataFormat'] = 'CAMEA-NEXUS-HDF5'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta, '/entry/start_time') 
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/entry/title')
    meta['datasetName']=proposal['name']+ "-" + \
                                 getDictItem(scientificmeta,'/entry/sample/name')
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['sample'] = getDictItem(scientificmeta, '/entry/sample/name')
    meta['scientificMetadata']=scientificmeta

    # CAMEA specific data
    meta['incident_energy'] = getDictItem(scientificmeta, '/entry/CAMEA/monochromator/energy')
    meta['nominal_analyser_energy'] = getDictItem(scientificmeta, 
                                                  '/entry/CAMEA/analyzer/nominal_energy')
    
    return meta
