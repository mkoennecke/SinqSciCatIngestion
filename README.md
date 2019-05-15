# SINQ SciCAT File Ingestion

This is a set of programs for ingesting SINQ data files into the SciCAT database. At the time of writing (04/2019)
this is a proof of concept implementation working only for SANS data files from 2017 and 2018. 

## Authors

- Mark Koennecke
- Stephan Egli


## How It Works

Ingestion is actually a two step process:

1. Detect the association between file numbers, proposals and datasets. This is the purpose of metaspan-detector.py
2. Using the list generated in step 1, actually ingest the data into SciCAT. This is done by scingest.py

## Span Detection

This happens in metaspan-detector.py. This programs iterates across a whole years worth of data. It detects proposal changes and 
datasets. The configuration of that program lives in the top of metaspan-detector.py for now. 

For detecting proposal changes it compares the experiment_identifier read from the current file with the last known value. If there 
is a change  a PROP line is output. 


For detecting dataset changes, metaspan-detector.py compares the current difference between files with the previous one. It then applies a series of 
tests in order to determine if the changes are significant or not.  This is done in the method isSignificant(). The results of this where finetuned 
against a listing of file differences as created by meta-diff.py. As of now, and for SANS, the results are reasonably accurate.  

## Actual Ingestion
This is scingest.py. It is fairly straight forward in that it parses the output from metaspan-detector, reads meta data and forwards this to 
SciCAT. 

There is a support program for ingestion, make-plot.py, which generates a png image of the data in the file. It uses the rainbow color map preferred 
by the instrument scientists.

## Support Files

**instruments.py** contains the instrument specific code for reading meta data from NeXus files and calculating signatures. It has two main 
entry points readMeta() and makeSignature(). Both are designed to be extended for further SINQ instruments. 

**sinqutils.py** contains some utility code for calculating SINQ file names

**levenshtein.py** is an implementation of the levenshtein algorith stolen from the WWW.


**SciCAT.py** contains the code for the actual ingestion int SciCAT. 

**meta-diff.py** is a program for locating the meta data differences in files and printing them. This is used to tune the algorithm in metaspan-detector.py

## Research Code

Prior to 2017 we did not have proposal information in SINQ data files. So, there is the task to detect a proposal change from the file meta 
data alone. To this purpose, two programs are available:

- tdiff-detector.py which iterates over a years worth of SINQ data and calculates various meta data differences of interest.
- anameta.py which reads the output from tdiff-detector and prints a difference list and a plot. 

An algorithm to properly detect proposal changes is still an open research question. Let us relax properly to reasonably accurate.

An older attempt at detecting meta data changes against a meta data signature rather then the full set, lives in  **span-detector.py**. This was not good enough, 
metaspan-detector.py is far more satisfactory. 

 