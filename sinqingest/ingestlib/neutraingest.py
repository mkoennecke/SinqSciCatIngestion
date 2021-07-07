""""
This module provides the ingestion meta data for NEUTRA

Mark Koennecke, July 2021
"""
import json
import time
from ingestlib.nicos_load import read_data
from pathlib import Path


def readIngestionData(filename, scicat, owner, accessGroups):
    try:
        fin = open(filename, 'rb')
        scientificmeta = read_data(filename, fin)
        fin.close()
    except:
        print('Failed to read %s' % filename)
        return None

    # We prefer the proposal data from the database
    proposalID = '20.500.11935/' + scientificmeta['Exp_proposal']
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = scientificmeta['Exp_localcontact']
        proposal['name'] = scientificmeta['Exp_users']
        proposal['title'] = scientificmeta['Exp_title']
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']=owner
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'NEUTRA at SINQ'
    meta['dataFormat'] = 'NICOS-SCAN'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=proposal['title']
    p = Path(filename)
    stat = p.stat()
    tt = time.localtime(stat.st_ctime)
    meta['creationTime'] = time.strftime('%Y-%m-%dT%H:%M:%S', tt)
    meta['datasetName']=p.name 
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['sample'] = scientificmeta['Sample_samplename']
    meta['scientificMetadata']=scientificmeta
    
    # NEUTRA specific additional meta data
    
    return meta
