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
    meta['title'] = str(entry['title'][0])
    meta['collection_description'] = str(entry['comment'][0])
    meta['start_time'] = str(entry['start_time'][0])
    meta['end_time'] = str(entry['end_time'][0])
    meta['instrument'] = np.string_('SANS')
    source = {}
    source['type'] = np.string_('Spallation Neutron Source')
    source['probe'] = np.string_('neutron')
    source['name'] = np.string_('SINQ at PSI')
    meta['source'] = source
    meta['wavelength'] = entry['SANS/Dornier-VS/lambda'][0]
    coll = {}
    coll['shape'] = np.string_('nxcylinder')
    coll['size'] = entry['SANS/collimator/length'][0]
    meta['collimator'] = coll
    detector = {}
    detector['sum'] = np.sum(entry['SANS/detector/counts'])
    detector['distance'] = entry['SANS/detector/x_position'][0]
    detector['polar_angle'] = 0.
    detector['azimuthal_angle'] = 0.
    detector['aequatorial_angle'] = 0.
    detector['x_pixel_size'] = 7.5
    detector['y_pixel_size'] = 7.5
    if pathExists(entry,'SANS/detector/beam_center_x'.split('/')):
        detector['beam_center_x'] = entry['SANS/detector/beam_center_x'][0]*7.5
        detector['beam_center_y'] = entry['SANS/detector/beam_center_y'][0]*7.5
    meta['detector'] = detector
    sample = {}
    sample['name'] = str(entry['sample/name'][0])
    sample['environment'] = str(entry['sample/environment'][0])
    sample['aequatorial_angle'] = 0.
    if pathExists(entry,'sample/temperature'.split('/')):
        sample['temperature'] = entry['sample/temperature'][0]
    else:
        sample['temperature'] = np.string_('UNKNOWN')
    if pathExists(entry,'sample/magnet'.split('/')):
        sample['magnet'] = entry['sample/magnet'][0]
    else:
        sample['magnet'] = np.string_('UNKNOWN')
    meta['sample'] = sample
    control = {}
    control['mode'] = entry['SANS/detector/count_mode'][0]
    control['preset'] = entry['SANS/detector/preset'][0]
    control['time'] = entry['SANS/detector/counting_time'][0]
    control['integral'] = entry['SANS/monitor1/counts'][0]
    control['monitor2'] = entry['SANS/monitor2/counts'][0]
    control['monitor3'] = entry['SANS/monitor3/counts'][0]
    meta['control'] = control
    meta['user'] = entry['user/name'][0]
    meta['experiment_identifier'] = str(entry['proposal_id'][0])
    meta['attenuator'] = entry['SANS/attenuator/selection'][0]
    f.close()
    return meta

def makeSANSSignature(meta):
    sample = meta['sample']
    det = meta['detector']              
    col = meta['collimator']
    signature = meta['title'] + meta['collection_description'] +sample['name'] +\
                sample['environment'] + ' ' + str(meta['wavelength']) + ' ' + str(det['distance']) +\
                ' ' + str(col['size'])
    return signature

    
