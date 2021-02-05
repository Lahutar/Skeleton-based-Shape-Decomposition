# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 11:07:24 2021

@author: Leo
"""


import mat2py

#import sys

'''
converts single point coordinates (nx2 double) to a list
'''
def coord2list_onept(nparr):
    tlist = list()
    for i in nparr:
        for j in range(1, len(i), 2):
            if i[j] > 0:
                tmp = (int(i[j-1]), int(i[j]))
                tlist.append(tmp)
    return tlist


'''
converts multi point coordinates (nxN double) to a list of lists
'''
def coord2list_multpt(nparr):
    tlist = list()
    for i in nparr:
        tmp2 = list()
        for j in range(1, len(i), 2):
            if i[j] > 0:
                tmp1 = (int(i[j-1]), int(i[j]))
                tmp2.append(tmp1)
        tlist.append(tmp2)
    return tlist


'''
if there is more than 1 point in an 8 nbr region:
    only keep the first one
'''
def reduce_coords(inlist):
  
    for i in inlist:  # create virtual neighbors, delete them if they exist
        if type(i) == tuple:
            for j, k in enumerate(inlist):
                if i != k and type(k) == tuple:
                    dx = abs(i[0] - k[0])
                    dy = abs(i[1] - k[1])
                    if dx + dy <= 2:
                        inlist[j] = 0
    outlist = [i for i in inlist if type(i) == tuple]
    return outlist


'''
read data from Bai skeletonization:
    bwd_skel (binary matrix of skeleton), contour (boundary of input shape), 
    endpoints (end points in skeleton), nodes (branching points in skeleton), 
    skel_list (list of all skeleton points), skel_dict (dictionary of skeleton points (by index in skel_list) and their contact points)
'''
def read_data(obj):
    matdata = mat2py.readmat(obj)
       
    # assign local variables
    bwd_skel = matdata['bwd_skel']
    clistmat = matdata['clist']
    contour = matdata['contour']
    endpoints = matdata['endpoints']
    nodes = matdata['nodes']
    shape = matdata['shape']
     
    # convert variables to proper format
    skel_list = list()
    skel_dict = dict()
    clist = coord2list_multpt(clistmat)
    contour = coord2list_onept(contour)
    nodes2 = coord2list_onept(nodes[:, [1, 2]])
    endpoints2 = coord2list_onept(endpoints[:, [1, 2]])
   
    # transform to dict (key = skeleton point,
    # value = associated boundary points)
    NOTFOUND = 0
    PSTACK = set()
    for sidx, scoords in enumerate(clist):  # skeleton points
        skel_list.append(scoords[0])
        idx = list()
        coords_red = reduce_coords(scoords[1:])
        for bpoint in coords_red:  # boundary points
            if (bpoint[1], bpoint[0]) in contour:
                # coordinates are reversed here
                idx.append((contour.index((bpoint[1], bpoint[0]))))
                PSTACK.add((bpoint[1], bpoint[0]))
            else:
                NOTFOUND += 1
            skel_dict[sidx] = idx
    
    return bwd_skel, contour, endpoints2, nodes2, skel_list, skel_dict

'''
read data for shape
'''
def read_shape(obj):
    matdata = mat2py.readmat(obj)
    shape = matdata['shape']
    contour = matdata['contour']
    contour = coord2list_onept(contour)
    return shape, contour
