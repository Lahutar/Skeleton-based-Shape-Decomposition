"""
author: leosel
"""
import math
import numpy as np
import scipy as sp
from scipy import ndimage
from shapely.geometry import Polygon
from matplotlib.path import Path
from smallestenclosingcircle import *

"""
function to compute the aspect ratio of a given polygon (object from shapely polygon class)
"""
def compute_aspectratio(polygon):
    contour = list(polygon.exterior.coords)
    boundingbox = polygon.bounds
    boundingcircle = make_circle(contour)

    #move polygon contour to corner
    moved_contour = []
    for i in range(len(contour)):
        moved_contour.append((contour[i][0]-boundingbox[0], contour[i][1]-boundingbox[1]))
    polygon_path = Path(moved_contour)

    #compute mask
    width, height = int(boundingbox[2] - boundingbox[0] + 2), int(boundingbox[3]-boundingbox[1]+2)
    y, x = np.mgrid[:height, :width]
    coors = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))
    mask = polygon_path.contains_points(coors)  # coors.shape is (4000000,2)
    reshaped_mask = mask.reshape(height, width)

    #compute distance transformation and find max distance
    dist = sp.ndimage.morphology.distance_transform_edt(reshaped_mask)
    max_dist = np.amax(dist)

    aspect_ratio = float(max_dist/boundingcircle[2])

    return aspect_ratio



"""
function to find all candidate cuts on an edge. 
candidates are skeleton points with two contact points on either side of the edge 
that lie between the bounds of the edge.
candidate: (coords of skeleton point, radius, contact points)
if bridges is True, the bounds of the edge and the two nodes are moved 2 places 
(not for end points in the skeleton)
"""
def find_candidates(data, edge, bridges=0):
    candidates = []

    # get the relations of the 2 bounds on the boundary
    relation = relation_bounds(edge.bound_from, edge.bound_to)

    # compute the bounds of the first and last node
    if bridges != 0:
        bound_from, bound_to = move_bounds(edge.bound_from, edge.bound_to, bridges, len(data.contour)-1)
        if edge.node_to.is_end:
            bound_to = edge.bound_to
        if bound_from is None or bound_to is None:
            print("could not move bounds")
            bound_from = edge.bound_from
            bound_to = edge.bound_to
    else:
        bound_from = edge.bound_from
        bound_to = edge.bound_to

    # include first node in candidate list
    candidates.append((edge.skel[bridges], data.image[edge.skel[bridges]], bound_from))

    # find all candidates between first and last node
    for i in range(bridges+1, len(edge.skel)-(bridges+1)):
        contact = sorted(data.contact_dict[data.skel_list.index(edge.skel[i])])
        p = None
        q = None
        # check if there are 2 contact points p and q such that
        # p is on one side of the polygon, q on the other side
        # depending on relations of bounds, compute p_list and q_list as the set of points on either side of the polygon
        # if both are not empty choose p and q and add a new candidate
        if relation == 1:
            p_list = [p for p in contact if bound_from[0] < p < bound_to[0]]
            if p_list:
                p = p_list[-1]
            q_list = [q for q in contact if bound_to[1] < q < bound_from[1]]
            if q_list:
                q = q_list[0]
        elif relation == 2:
            p_list = [p for p in contact if bound_from[0] < p < bound_to[0]]
            if p_list:
                p = p_list[-1]
            q_list1 = [q for q in contact if bound_from[1] > q]
            q_list2 = [q for q in contact if bound_to[1] < q]
            if q_list2:
                q = q_list2[0]
            elif q_list1:
                q = q_list1[0]
        else:
            p_list1 = [p for p in contact if bound_from[0] < p]
            p_list2 = [p for p in contact if bound_to[0] > p]
            if p_list2:
                p = p_list2[-1]
            elif p_list1:
                p = p_list1[-1]
            q_list = [q for q in contact if bound_to[1] < q < bound_from[1]]
            if q_list:
                q = q_list[0]
        if p is not None and q is not None:
            candidates.append((edge.skel[i], data.image[edge.skel[i]], (p, q)))

    # include the last node in candidate list
    candidates.append((edge.skel[-1-bridges], data.image[edge.skel[-1-bridges]], bound_to))

    return candidates


"""
function to get the relation between two bounds based on the circular list of the boundary
"""
def relation_bounds(b1, b2):
    if b1[0] <= b2[0]:
        if b1[1] >= b2[1]:
            return 1  #end of list outside bounded polygon
        else:
            return 2  #end of list between b1[1] and b2[1]
    else:
        if b1[1] >= b2[1]:
            return 3  #end of list between b1[0] and b2[0]


"""
function to move the two bounds b1,b2 the given number of steps. 
compute new position based on the list length
"""
def move_bounds(b1, b2, steps, listlength):
    if b1[0] <= b2[0]:
        if b2[0] - b1[0] < 2 * steps:
            return None, None
        else:
            new_b1_0 = move_bound(b1[0], listlength, steps, 1)
            new_b2_0 = move_bound(b2[0], listlength, steps, 0)
    else:
        if listlength - b1[0] + b2[0] < 2 * steps:
            return None, None
        else:
            new_b1_0 = move_bound(b1[0], listlength, steps, 1)
            new_b2_0 = move_bound(b2[0], listlength, steps, 0)
    if b2[1] <= b1[1]:
        if b1[1] - b2[1] < 2 * steps:
            return None, None
        else:
            new_b1_1 = move_bound(b1[1], listlength, steps, 0)
            new_b2_1 = move_bound(b2[1], listlength, steps, 1)
    else:
        if listlength - b2[1] + b1[1] < 2 * steps:
            return None, None
        else:
            new_b1_1 = move_bound(b1[1], listlength, steps, 0)
            new_b2_1 = move_bound(b2[1], listlength, steps, 1)
    return (new_b1_0, new_b1_1), (new_b2_0, new_b2_1)


"""
function to move the bound b <steps> places to the left (smaller/direction=0) or right (larger/direction=1)
"""
def move_bound(b, listlength, steps=1, direction=1):
    if direction == 0:
        if b <= steps:
            return steps-b
        else:
            return b-steps
    if direction == 1:
        if (listlength-b) < steps:
            return b+steps-listlength-1
        else:
            return b+steps

"""
check if lies between bound1 and bound3. If so, the polygon between bound1 and bound 2 is ok. 
"""
def check_relation_bounds(bound1,bound2,bound3):
    if relation_bounds(bound1, bound3) == 1:
        if bound1[0] < bound2[0] and bound2[1] < bound1[1]:
            return True
    elif relation_bounds(bound1, bound2) == 3:
        if (bound1[0] < bound2[0] or bound2[0] <= bound3[0]) and bound2[1] < bound1[1]:
            return True
    elif relation_bounds(bound1, bound3) == 2:
        if bound1[0] < bound2[0] and (bound2[1] < bound1[1] or bound2[1] >= bound3[1]):
            return True


"""
returns polygon contour as circular list
bounds= (node A, 1. bound A, 1. bound B, node B, 2. bound B, 2. bound A) 
"""
def bounds_to_polygon(bounds,data_contour):
    if bounds[2] == bounds[4]: #endbranch
        if bounds[1] <= bounds[2] and bounds[4] <= bounds[5]:
            contour = [bounds[0]]+data_contour[bounds[1]:(bounds[5]+1)]+[bounds[0]]
        else:
            contour = [bounds[0]]+data_contour[bounds[1]:]+data_contour[:(bounds[5]+1)]+[bounds[0]]
    else: #inner branch
        if bounds[1] > bounds[2]: #end of circular list in between 1 and 2
            contour = [bounds[0]]+data_contour[bounds[1]:]+data_contour[:(bounds[2]+1)]+[bounds[3]]+data_contour[bounds[4]:(bounds[5]+1)]+[bounds[0]]
        elif bounds[5] < bounds[4]: #end of circular list in between 4 and 5
            contour = [bounds[0]]+data_contour[bounds[1]:(bounds[2]+1)]+[bounds[3]]+data_contour[bounds[4]:]+data_contour[:(bounds[5]+1)]+[bounds[0]]
        else: #end of circular list somewhere else
            contour = [bounds[0]]+data_contour[bounds[1]:(bounds[2]+1)]+[bounds[3]]+data_contour[bounds[4]:(bounds[5]+1)]+[bounds[0]]
    return contour

"""
rotate list <steps>-many places
"""
def rotate(inlist, steps):
    return inlist[steps:] + inlist[:steps]

"""
rotate contour such that the new beginning lies either
a) midway through the contour if its an endbranch or
b) midway through the longer side
"""
def rotate_contour(contour, midpoint, midbounds):  # rotate such that the new beginning lies midway through the contour
    #compute number of steps for rotation
    if midbounds[0] == midbounds[1]:
        steps = math.floor((len(contour)) / 2)
    else:
        length1 = contour.index(midpoint)
        length2 = len(contour) - length1
        if length1 < length2:
            steps = length1 + math.floor(length2 / 2)
        else:
            steps = math.floor(length1 / 2)
    rotated_contour = rotate(contour, steps)
    return rotated_contour