""""
This module provides the ingestion meta data for ZEBRA

Mark Koennecke, July 2021
"""
import json
import os
from ingestlib.hdf_reader import hdf5ToDict
from ingestlib.sinqutils import getDictItem
from ingestlib.readsinqascii import readSINQAscii, clean_data
from pathlib import Path


def readCCLMeta(filename):
    meta = {}
    f = open(filename, 'r')
    dataset = ["date", "instrument", "user" , "proposal_email", "title", "sample", "temperature", "ProposalID", "stt", "chi", "phi", "om", "nu"]
    for line in f:
        if line.startswith('#data'):
            break
        extractedData = line.split('=')
        if len(extractedData) == 2:
            key = extractedData[0].strip()
            if key in dataset:
                meta[key] = extractedData[1].strip()
        meta['detector_mode'] = '1d'        
        f.close()
        return meta

def prepareHDFIngest(scientificmeta, scicat, owner, accessGroups):
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
    meta['creationLocation'] = 'ZEBRA at SINQ'
    meta['dataFormat'] = 'ZEBRA-NEXUS-HDF5'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta, '/entry1/start_time') 
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/entry1/title')
    p = Path(scientificmeta['filename'])
    meta['datasetName']= p.name
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['scientificMetadata']=scientificmeta
    meta['temperature'] = getDictItem(scientificmeta, '/entry1/sample/temperature')
    meta['magnetic_field'] = getDictItem(scientificmeta, '/entry1/sample/mf')
    meta['sample'] = getDictItem(scientificmeta, '/entry1/sample/name')

    # ZEBRA specific data
    return meta

def prepareDATIngest(scientificmeta, scicat, owner, accessGroups):
    proposalID = '20.500.11935/' + getDictItem(scientificmeta, '/ProposalID').replace(' ', '')
    res = scicat.read_proposal(proposalID)
    if res:
        proposal = json.loads(r.txt)
    else:
        # no proposal data from the DB, use file meta data instead
        proposal = {}
        proposal['pi_email'] = getDictItem(scientificmeta,'/proposal_user')
        proposal['name'] = getDictItem(scientificmeta, '/user')
        proposal['title'] = getDictItem(scientificmeta, '/title')
        proposal['proposalID'] = proposalID
        proposal['ownerGroup']=owner
        proposal['accessGroups']=accessGroups

    meta = {}
    meta['principalInvestigator']=proposal['pi_email']
    meta['creationLocation'] = 'ZEBRA at SINQ'
    meta['dataFormat'] = 'SINQ-ASCII'
    meta['sourceFolder'] = ''
    meta['owner']=proposal['name']
    meta['ownerEmail']=proposal['pi_email']
    meta['creationTime'] = getDictItem(scientificmeta,'/date').replace(' ', 'T')
    meta['contactEmail'] = proposal['pi_email']
    meta['type']='raw'
    meta['description']=getDictItem(scientificmeta, '/title') + '-' + getDictItem(scientificmeta, '/sample')
    p = Path(scientificmeta['filename'])
    meta['datasetName']=p.name 
    meta['ownerGroup']=proposal['ownerGroup']
    meta['accessGroups']=proposal['accessGroups']
    meta['proposalId']=proposalID
    meta['sample'] = getDictItem(scientificmeta, '/sample')
    meta['scientificMetadata']=scientificmeta

    meta['wavelength'] = getDictItem(scientificmeta, '/wavelength')

    return meta
    

def readIngestionData(filename, scicat, owner, accessGroups):
    file_type = 'hdf'
    real_filename = filename
    try:
        if os.path.exists(filename):
            scientificmeta = hdf5ToDict(filename)
        else:
            file_type = 'dat' 
            filename = filename.replace(".hdf", ".dat")
            if os.path.exists(filename):
                real_filename = filename
                scientificmeta = readSINQAscii(filename)
                scientificmeta = clean_data(scientificmeta)
            else:
                filename = filename.replace(".dat", ".ccl")
                if os.path.exists(filename):
                    real_filename = filename
                    scientificmeta = readCCLMeta(filename)
                else:
                    raise Exception('No valid file format found')
    except:
        print('Failed to read %s' % filename)
        return None

    scientificmeta['filename'] = real_filename
    if file_type == 'hdf':
        meta = prepareHDFIngest(scientificmeta, scicat, owner, accessGroups)
    else:
        meta = prepareDATIngest(scientificmeta, scicat, owner, accessGroups)
    meta['real_filename'] = real_filename
    
    return meta
