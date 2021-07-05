""""
This module provides the ingestion meta data for ORION

Mark Koennecke, July 2021
"""
import json
from ingestlib.sinqutils import getDictItem
from ingestlib.readsinqascii import readSINQAscii, clean_data
from pathlib import Path


def readIngestionData(filename, scicat, owner, accessGroups):
    try:
        scientificmeta = readSINQAscii(filename)
    except:
        print('Failed to read %s' % filename)
        return None

    scientificmeta = clean_data(scientificmeta) 

    # We prefer the proposal data from the database
    proposalID = '20.500.11935/' + getDictItem(scientificmeta, '/ProposalID').replace(' ', '')
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = 'Oksana.Zaharko@psi.ch'
        proposal['name'] = getDictItem(scientificmeta, '/User')
        proposal['title'] = getDictItem(scientificmeta, '/Title')
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']=owner
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'ORION at SINQ'
    meta['dataFormat'] = 'SINQ-ASCII'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta,'/File Creation Date').replace(' ', 'T')
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/Title')
    p = Path(filename)
    meta['datasetName']=p.name 
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['sample'] = getDictItem(scientificmeta, '/Sample Name')
    meta['scientificMetadata']=scientificmeta
    
    return meta
