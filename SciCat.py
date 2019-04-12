"""
   This is the interface to SciCat for the SINQ ingestor for SINQ file data

   Mark Koennecke, April 2019 
"""
import json 

class SciCat(object):
    def writeProposal(self,meta):
# TODO: Find the proposal in DUO and enter its meta data into the SciCat DB
# Use experiment_identifier or start_time in meta for association
# There can be errors, there can be internal stuff. 
        print('Dumping proposal')

    def writeDataset(self,start,end, meta):
# TODO :ingest a dataset ranging from start - end with meta data as in the meta dictionary
        #for num in range(start,end):
        #   fname = makeFilename(froot,2018,'sans',num,'hdf')
        #   subtract froot from fname
        #   append to file list
        # print(meta)
        print(json.dumps(meta, indent=3, sort_keys=True))
        print('Dumping Dataset ranging from %d to %d' %(start,end))

            # y['sourceFolder']=fullPath
            #     # todo: this is only correct for single file datasets
            #     y['size']=os.stat(fullPath).st_size
            #     # correct for timezone
            #     if 'file_time' in x:
            #         y['creationTime'] = x['file_time']+'+01:00'
            #     y['type']='raw'
            #     y['license'] = 'CC BY-SA 4.0'
            #     pprint(y)
            #     dsResponse = swagger_client.DatasetApi().dataset_create(data=y)
            #     print "Resulting pid:",dsResponse.pid

            #     raw={}
            #     raw['id']=dsResponse.pid
            #     if 'owner' in x:
            #         raw['principalInvestigator']=x['owner']
            #     else:
            #         raw['principalInvestigator']='Unknown'
            #     if 'file_time' in x:
            #         raw['creationTime'] = x['file_time']+'+01:00'
            #     if 'instrument' in x:
            #         raw['creationLocation']='/PSI/SINQ/'+x['instrument']
            #     if 'NeXus_version' in x:
            #         raw['dataFormat']='NeXus_version '+x['NeXus_version']
            #     raw['scientificMetadata']=x['entry1']
            #     raw['datasetId']=dsResponse.pid


