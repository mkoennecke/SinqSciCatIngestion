"""
   This is the interface to SciCat for the SINQ ingestor for SINQ file data

   Mark Koennecke, April 2019 
"""

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

        print('Dumping Dataset ranging from %d to %d' %(start,end))


