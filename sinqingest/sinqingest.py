#!/usr/bin/env python3
"""
This is the ingestion program for SINQ data files. It can
ingest a range of files into the SciCat file database.

Usage:

    sinqingest.py config.json <start-numor> <end-numor> 

Mark Koennecke, July 2021

using previous work from myself, Stephan Egli and Philip Hertl
"""
import pdb

import json
import sys
import importlib
from ingestlib.sinqutils import SinqFileList
from ingestlib.scicat import SciCat

if len(sys.argv) < 3:
    print("Usage:\n\tsinqingest.py config.json start-numor end-numor")
    sys.exit(1)

#------------- load configuration
with open(sys.argv[1], 'r') as fin:
    txt = fin.read()
config = json.loads(txt)

#--------- load meta data reader
# These are expected to live in a module named <inst>ingest.py
# This module has to provide a method:
#     readIngestionData(filename, SciCat, 
#                        owner-group, access-groups)
# This function has to return a dictionary with the properly
# formated ingestion meta data for the filename passed in
#
# Yhe owner-group and acess-groups are used when the same data from the 
# proposal is not available
ingestModule = importlib.import_module('ingestlib.%singest' % config['instrument'])


#----- Prepare file iterator
fullroot = config['root'] + '/' + config['year'] + '/' + config['instrument']
sq = SinqFileList(fullroot, int(config['year']), config['instrument'], config['extension'],
                  int(sys.argv[2]), int(sys.argv[3]))
sqiter = iter(sq)

#pdb.set_trace()
#--------- Prepare connection to SciCat
sc = SciCat(config['scicat-url'])
sc.loginPSI(config['user'], config['password'])

#------------------------- iterate through files
numor, fname = next(sqiter)
while fname:
    print(fname)
    ingestmeta = ingestModule.readIngestionData(fname, sc, 
                                                    config['owner-group'],
                                                    config['access-groups'])
    if ingestmeta:
        ingestmeta['sourceFolder'] = fullroot
        datablock = sc.package_file(fname)
        status = sc.dataset_post(ingestmeta)
        if 'error' in status:
            print('Error ingesting %s, %s' % (fname, status))
        else:
            status = sc.origdatablock_post(status['pid'], datablock)
            if 'error' in status:
                print('Error ingesting datablock for %s, %s' % (fname, status))
    else:
        print('File %s could not be read' % fname)
    numor, fname = next(sqiter)



