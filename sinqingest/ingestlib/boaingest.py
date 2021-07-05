""""
This module provides the ingestion meta data for BOA

Mark Koennecke, July 2021
"""
import json
from ingestlib.hdf_reader import hdf5ToDict
from ingestlib.sinqutils import getDictItem

def readIngestionData(filename, scicat, owner, accessGroups):
    try:
        scientificmeta = hdf5ToDict(filename)
    except Exception as e:
        print('Failed to read %s with %s' % (filename, e))
        return None
    
    # We prefer the proposal data from the database
    proposalID = '20.500.11935/' + getDictItem(scientificmeta, '/entry1/proposal_id').replace(' ', '')
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = getDictItem(scientificmeta, '/entry/buser/email')
        proposal['name'] = getDictItem(scientificmeta, '/entry/user/name')
        proposal['title'] = getDictItem(scientificmeta, '/entry/title')
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']='owner'
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'BOA at SINQ'
    meta['dataFormat'] = 'BOA-NEXUS-HDF5'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta, '/entry/start_time') 
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/entry/title')
    temp=getDictItem(scientificmeta,'/entry/sample/temperature')
    meta['datasetName']=proposal['name']+ "-" + \
                                 getDictItem(scientificmeta,'/entry/sample/name') \
                                 + "-T=" +temp
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['sample'] = getDictItem(scientificmeta, '/entry/sample/name')
    meta['scientificMetadata']=scientificmeta

    return meta
