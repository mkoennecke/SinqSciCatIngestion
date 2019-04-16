"""
   This is the interface to SciCat for the SINQ ingestor for SINQ file data

   Mark Koennecke, April 2019 
"""
import json 
from sinqutils import makeSINQrelFilename
import urllib.parse
import requests
import subprocess

class SciCat(object):
    def writeProposal(self,meta):
        print('Dumping proposal not needed, instead need to verify if already in SciCat')

    def writeDataset(self, root, year, inst, postfix, start, end, scientificmeta, token):

        print('Dumping Dataset ranging from %d to %d' %(start,end))
        # create filelisting file

        # TODO add year to root for sourceFolder ?
        filenameList='intermediate/filelisting-'+str(year)+'-'+str(start)+'.txt'
        filelist = open(filenameList,'w') 
        for num in range(start,end+1):
           fname = makeSINQrelFilename(int(year),inst,int(num),postfix)
           print(fname)
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

            meta = {}
            meta['principalInvestigator']=proposal['pi_email']
            meta['creationLocation'] = proposal['MeasurementPeriodList'][0]['instrument']
            meta['dataFormat'] = 'SANS-NEXUS-HDF5'
            meta['sourceFolder'] = root
            meta['owner']=proposal['firstname']+proposal['lastname']
            meta['ownerEmail']=proposal['email']
            meta['type']='raw'
            # TODO decide what fields to add to description
            meta['description']=scientificmeta['title']+" / collection:"+scientificmeta['collection_description']
            temp='undefined'
            if 'temperature' in scientificmeta['sample']:
                tempCandidate=scientificmeta['sample']['temperature']
                if isinstance(tempCandidate, float):
                    temp='%.1f' % tempCandidate
               
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