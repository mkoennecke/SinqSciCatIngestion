""""
This module provides the ingestion meta data for TASP

Mark Koennecke, July 2021
"""
import json
import time
from ingestlib.sinqutils import getDictItem
from ingestlib.readsinqascii import readILLAscii, clean_data
from pathlib import Path


def readIngestionData(filename, scicat, owner, accessGroups):
    try:
        scientificmeta = readILLAscii(filename)
    except:
        print('Failed to read %s' % filename)
        return None

    scientificmeta = clean_data(scientificmeta) 

    # We prefer the proposal data from the database
    proposalID = '20.500.11935/' + getDictItem(scientificmeta, '/PARAM:ProposalID').replace(' ', '')
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = 'Uwe.Stuhr@psi.ch'
        proposal['name'] = getDictItem(scientificmeta, '/USER_')
        proposal['title'] = getDictItem(scientificmeta, '/TITLE')
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']=owner
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'EIGER at SINQ'
    meta['dataFormat'] = 'ILL-ASCII'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/TITLE')
    p = Path(filename)
    stat = p.stat()
    tt = time.localtime(stat.st_ctime)
    meta['creationTime'] = time.strftime('%Y-%m-%dT%H:%M:%S', tt)
    meta['datasetName']=p.name 
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    #meta['sample'] = getDictItem(scientificmeta, '/Sample Name')
    meta['scientificMetadata']=scientificmeta
    
    # TAS specific additional meta data
    meta['temperature'] = getDictItem(scientificmeta, '/VARIA:TT')
    meta['magnetic_field'] = getDictItem(scientificmeta, '/VARIA:MF')
    meta['QE'] = getDictItem(scientificmeta, '/POSQE')
    meta['command'] = getDictItem(scientificmeta, '/COMND')
    
    return meta
