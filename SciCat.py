"""
   This is the interface to SciCat for the SINQ ingestor for SINQ file data

   Mark Koennecke, April 2019 
"""
import json 
from sinqutils import makeSINQFilename
from sinqutils import makeSINQrelFilename
import urllib.parse
import requests
import subprocess
import sys
import numpy as np
import matplotlib.pyplot as plt
import h5py
import os.path
from matplotlib.colors import ListedColormap

class SciCat(object):
    def writeProposal(self,meta):
        print('Dumping proposal not needed, instead need to verify if already in SciCat')

    def createAttachmentFile(self, root, year, inst, postfix, start):
        rainbow = np.ones((256,4))
        rf = open('rainbow.rgb','r')
        for i in range(0,256):
            r = int(rf.readline())
            g = int(rf.readline())
            b = int(rf.readline())
            # important enforce float values !
            rainbow[i,0] = r/256.0
            rainbow[i,1] = g/256.0
            rainbow[i,2] = b/256.0
        rf.close()

        rainmap = ListedColormap(rainbow)
        dfile = makeSINQFilename(root,int(year),inst,int(start),postfix)
        f5 = h5py.File(dfile,'r')
        ds = f5['entry1/data1/counts']
        try:
            plt.imshow(ds,rainmap)
            # plt.show()
            tmp = os.path.basename(dfile)
            fname = 'intermediate/'+tmp + '.png'
            print('Saved attachment image to ' + fname)
            plt.savefig(fname)
            plt.close()
            f5.close()
            return fname
        except:
            return ""


    def writeDataset(self, root, year, inst, postfix, start, end, scientificmeta, token, attachmentFile):

        print('Dumping Dataset ranging from %d to %d' %(start,end))
        # create filelisting file

        # TODO add year to root for sourceFolder ?
        filenameList='intermediate/filelisting-'+str(year)+'-'+str(start)+'.txt'
        filelist = open(filenameList,'w') 
        for num in range(start,end+1):
           fname = makeSINQrelFilename(int(year),inst,int(num),postfix)
           print(fname)
           filelist.write(fname+"\n")
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
            # run datasetIngestor command including attachments
            if (attachmentFile !=""):
                subprocess.call(["datasetIngestor","-addattachment", attachmentFile,"-testenv", "-ingest", "-allowexistingsource", "-token", token, filenameMeta, filenameList])
            else:
                subprocess.call(["datasetIngestor","-testenv", "-ingest", "-allowexistingsource", "-token", token, filenameMeta, filenameList])

             # todo remove files in "intermediate" folder

