"""
  This file contains procedures for extracting meta data from SINQ files. What is extracted is
  determined from two sources:
  - the instrument scientist
  - the NeXus application definition for the instrument type. This is also the reference for all 
    names

  The return is always a dictionary of names and values. 

  Mark Koennecke, April 2019
"""

import h5py
import numpy as np

def decodeHDF(va):
    # turn byte strings to normal strings
    if isinstance(va, bytes):
        try:
            resultValue = va.decode("utf-8")
            pass
        except Exception as e:
            resultValue = va.decode("latin1")
        return resultValue
    elif isinstance(va, np.ndarray):
        # convert byte arrays to string array
        newArray = []
        for a in va:
            if isinstance(a, bytes):
                newArray.append(a.decode("utf-8"))
            else:
                newArray.append(a)
        return newArray
    elif isinstance(va, np.float) and math.isnan(va):
        return None
    else:
        return va.item()

def readMetaData(filename):
    if filename.find('sans') >= 0:
        return readSANS(filename)
    else:
        raise NotImplemented

def makeSignature(meta):
    if meta['instrument'] == b'SANS':
        return makeSANSSignature(meta)
    else:
        raise NotImplemented

def pathExists(root,path):
    if len(path) == 0:
        return True
    nextobj = path[0]
    if nextobj in root:
        nextroot = root[nextobj]
        newpath = path[1:]
        return pathExists(nextroot,newpath)
    else:
        return False

def readSANS(filename):
    f = h5py.File(filename,'r')
    meta = {}
    entry = f['entry1']
    meta['title'] = decodeHDF(entry['title'][0])
    meta['collection_description'] = decodeHDF(entry['comment'][0]).strip()
    # todo normalize times to RFC format
    meta['start_time'] = decodeHDF(entry['start_time'][0])
     # todo normalize times to RFC format
    meta['end_time'] = decodeHDF(entry['end_time'][0])
    meta['instrument'] = 'SANS'
    source = {}
    source['type'] = 'Spallation Neutron Source'
    source['probe'] = 'neutron'
    source['name'] = 'SINQ at PSI'
    meta['source'] = source
    meta['wavelength'] = decodeHDF(entry['SANS/Dornier-VS/lambda'][0])
    coll = {}
    coll['shape'] = 'nxcylinder'
    coll['size'] = decodeHDF(entry['SANS/collimator/length'][0])
    meta['collimator'] = coll
    detector = {}
    # todo find proper transformation detector['sum'] = np.sum(decodeHDF(entry['SANS/detector/counts']))
    detector['distance'] = decodeHDF(entry['SANS/detector/x_position'][0])
    detector['polar_angle'] = 0.
    detector['azimuthal_angle'] = 0.
    detector['aequatorial_angle'] = 0.
    detector['x_pixel_size'] = 7.5
    detector['y_pixel_size'] = 7.5
    if pathExists(entry,'SANS/detector/beam_center_x'.split('/')):
        detector['beam_center_x'] = decodeHDF(entry['SANS/detector/beam_center_x'][0])*7.5
        detector['beam_center_y'] = decodeHDF(entry['SANS/detector/beam_center_y'][0])*7.5
    meta['detector'] = detector
    sample = {}
    sample['name'] = decodeHDF(entry['sample/name'][0])
    sample['environment'] = decodeHDF(entry['sample/environment'][0])
    sample['aequatorial_angle'] = 0.
    if pathExists(entry,'sample/temperature'.split('/')):
        sample['temperature'] = decodeHDF(entry['sample/temperature'][0])
    else:
        sample['temperature'] = 'UNKNOWN'
    if pathExists(entry,'sample/magnet'.split('/')):
        sample['magnet'] = decodeHDF(entry['sample/magnet'][0])
    else:
        sample['magnet'] = 'UNKNOWN'
    meta['sample'] = sample
    control = {}
    control['mode'] = decodeHDF(entry['SANS/detector/count_mode'][0])
    control['preset'] = decodeHDF(entry['SANS/detector/preset'][0])
    control['time'] = decodeHDF(entry['SANS/detector/counting_time'][0])
    control['integral'] = decodeHDF(entry['SANS/monitor1/counts'][0])
    control['monitor2'] = decodeHDF(entry['SANS/monitor2/counts'][0])
    control['monitor3'] = decodeHDF(entry['SANS/monitor3/counts'][0])
    meta['control'] = control
    meta['user'] = decodeHDF(entry['user/name'][0])
    meta['experiment_identifier'] = decodeHDF(entry['proposal_id'][0])
    # todo: commented because not existing: meta['attenuator'] = decodeHDF(entry['SANS/attenuator/selection'][0])
    f.close()
    return meta

def makeSANSSignature(meta):
    sample = meta['sample']
    det = meta['detector']              
    col = meta['collimator']
    signature = meta['title'] + meta['user'] + meta['collection_description'] +sample['name'] +\
                sample['environment'] + ' ' + str(meta['wavelength']) + ' ' + str(det['distance']) +\
                ' ' + str(col['size'])
    return signature


def metaRecurse(root,meta):
    for key,val in meta.items():
        if isinstance(val,dict):
            newroot = root + '/' + key
            metaRecurse(newroot,val)
        else:
            print(root + '/' + key + '=' + str(val))
    
def printMeta(numor,meta):
    print('################## MetaData for: ' + str(numor))
    metaRecurse('',meta)
        
    
