### This is the Gaussian data smoothing function I wrote ###
import numpy

def smoothListGaussian(list,degree=5):  
    window=degree*2-1  
    weight=numpy.array([1.0]*window)  
    weightGauss=[]  

    for i in range(window):  
        i=i-degree+1  
        frac=i/float(window)  
        gauss=1/(numpy.exp((4*(frac))**2))  
        weightGauss.append(gauss)  
  
    weight=numpy.array(weightGauss)*weight  
    smoothed=[0.0]*(len(list)-window)  

    for i in range(len(smoothed)):  
        smoothed[i]=sum(numpy.array(list[i:i+window])*weight)/sum(weight)  

    return smoothed  

 
