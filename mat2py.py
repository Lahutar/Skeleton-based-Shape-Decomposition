# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 13:22:35 2017

@author: robwey/tehw0lf (https://www.github.com/tehw0lf)
"""
import h5py
import numpy
from scipy import io


def readmat(fname):
    try:
        matdata = io.loadmat(fname)
        #print('data loaded, old format')
    except NotImplementedError:
        matdata = {}
        fdata = h5py.File(fname, 'r').items()
            
        for i,j in fdata:
            tmpdata = numpy.array(j.value)
            matdata[i] = numpy.transpose(tmpdata)
        #print('data loaded, new format')
    return matdata


if __name__ == '__main__':
    data_new = readmat('matlab_new.mat')
    locals().update(data_new)
