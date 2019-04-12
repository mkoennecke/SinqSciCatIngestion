"""
  This is a number of utilities for working with SINQ data files. This was developed in 
  the context of the SciCAT indexing project.

  Mark Koennecke, April 2019 
"""

def makeSINQFilename(root,year,inst,numor,postfix):
    hundreds = abs(numor/1000)
    return '%s/%03d/%s%4dn%06d.%s' % (root,hundreds,inst,year,numor,postfix)

def makeSINQrelFilename(year,inst,numor,postfix):
    hundreds = abs(numor/1000)
    return '%03d/%s%4dn%06d.%s' % (hundreds,inst,year,numor,postfix)


"""
   This class provides an iterator for iterating over SINQ data files. 
"""
class SinqFileList(object):
    def __init__(self,root,year,inst,postfix,start,end):
        self.start = start
        self.end = end
        self.root = root
        self.inst = inst
        self.postfix = postfix
        self.year = year

    def __iter__(self):
        self.current = self.start
        return self

    def __next__(self):
        self.current = self.current + 1
        if self.current > self.end:
            raise StopIteration
        else:
            return self.current, makeSINQFilename(self.root,self.year,self.inst,self.current,self.postfix)


    def next(self):
        return self.__next__()

