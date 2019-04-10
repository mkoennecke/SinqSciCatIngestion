# SINQ SciCAT File Ingestion

This is a set of programs for ingesting SINQ data files into the SciCAT database. At the time of writing (04/2019)
this is a proof of concept implementation working only for SANS data files from 2017 and 2018. 

## Authors

- Mark Koennecke
- Stephan Egli


## How It Works

Ingestion is actually a two step process:

1. Detect the association between file numbers, proposals and datasets. This is the purpose of span-detector.py
2. Using the list generated in step 1, actually ingest the data into SciCAT. This is done by scingest.py

## Span Detection

This happens in span-detector.py. This programs iterates across a whole years worth of data. It detects propsal changes and 
datasets. The configuration of that program lives in the top of span-detector.py for now. 

For detecting proposal changes it compares the experiment_identifier read from the current file with the last known value. If there 
is a change  a PROP line is output. 

For detecting dataset changes, span-detector calculates a data signature by concatenating the most important experiment meta data. These 
signatures are compared by calculating their edit distance. If the edit distance is above a threshold, it is assumed that a major change 
has happened and a new dataset has started. A DS line is output in this case. For calculating the edit distance, the levenshtein 
algorithm is used.

## Actual Ingestion
This is scingest.py. It is fairly straight forward in that it parses the output from span-detector, reads meta data and forwards this to 
SciCAT. 


## Support Files

**instruments.py** contains the instrument specific code for reading meta data from NeXus files and calculating signatures. It has two main 
entry points readMeta() and makeSignature(). Both are designed to be extended for further SINQ instruments. 

**sinqutils.py** contains some utility code for calculating SINQ file names

**levenshtein.py** is an implementation of the levenshtein algorith stolen from the WWW.


**SciCAT.py** contains the code for the actual ingestion int SciCAT. 

## Research Code

Prior to 2017 we did not have proposal information in SINQ data files. So, there is the task to detect a proposal change from the file meta 
data alone. To this purpose, two programs are available:

- tdiff-detector.py which iterates over a years worth of SINQ data and calculates various meta data differences of interest.
- anameta.py which reads the output from tdiff-detector and prints a difference list and a plot. 

An algorithm to properly detect proposal changes is still an open research question. Let us relax properly to reasonably accurate.

 

 