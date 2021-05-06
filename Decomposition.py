"""
@author: leosel
"""
from Graph import *
from DecompositionHelper import *

import math
import numpy as np
from shapely.geometry import Polygon

import time

"""
Decomposition Algorithms with different approaches, constraints and optimizations
1) approaches:
- decomposition into skeleton branches
- linear decomposition on skeleton branches
- decomposition including bridges
2) constraints:
- min/max area
- fatness (atm not included)
3) optimization goals 
- minimize number of components (min_num) 
- maximize fatness (max_fat)
- minimize cut length (min_cut) (atm not included)
"""


"""
general decomposition approach for min/max area. 
the polygon cannot be decomposed if its area is smaller than the lower bound. 
if its area is smaller than the upper bound, decompose it into its branches but not further.
otherwise decompose the branches with the linear algorithm.
"""
def decomposition(data, min_area=0, max_area=math.inf, opt = 'min_num', bridges=0):
    polygon_area = data.object_area()
    if polygon_area < min_area:
        print("polygon too small for decomposition")
        polygon_decomposition = []
    elif polygon_area < max_area:
        polygon_decomposition = tree_decomposition(data, min_area, max_area)
    else:
        polygon_decomposition, partial = branch_decomposition(data, min_area, max_area, opt, bridges)
    return polygon_decomposition

"""
decompose polygon into subpolygons belonging to the branches of the skeleton tree. 
keep only subpolygons of the correct size
"""
def tree_decomposition(data, min_area=0, max_area=math.inf):
    polygon_decomposition = []
    for branch in data.edges:
        branch_poly = Polygon(branch.poly_contour)
        if min_area <= branch_poly.area <= max_area:
            polygon_decomposition.append(branch_poly)
    return polygon_decomposition

"""
compute decompositions for each branch individually
"""
def branch_decomposition(data, min_area=0, max_area=math.inf, opt = 'min_num', bridges=0):
    polygon_decomposition = []
    partial = False
    start_time = int(time.time()/60)
    for edge in data.edges:
        edge_decomposition = linear_decomposition(data, edge, min_area, max_area, opt, bridges)
        polygon_decomposition = polygon_decomposition + edge_decomposition
        current_time = int(time.time()/60)
        delta_time = current_time - start_time
        if delta_time > 5:
            partial = True
            break
    return polygon_decomposition, partial

"""
compute decomposition based on a linear skeleton
array check contains either some optimal value or is inf if no feasible decomposition exists
array cut contains information for backtracking and computation of partition
"""
def linear_decomposition(data, edge, min_area = 0, max_area = math.inf, opt = 'min_num', bridges=0):
    candidates = find_candidates(data, edge, bridges)

    if candidates == []:
        return []
    n = len(candidates)
    # define 2 arrays and initialize
    check = np.array([None]*n)
    cuts = np.array([[None]*2]*n)
    check[n-1] = 0
    # fill arrays iteratively from n-2 to 0
    for i in range(n-2, -1, -1):
        # compute feasible cuts between i and n
        feasible_cuts = []
        for j in range(i+1, n):
            # check if polygon between j and n has feasible decomposition
            if check[j] is not math.inf and check[j] is not None:
                # check if polygon between i and j is simple and has no overlapping edges
                if check_relation_bounds(candidates[i][2], candidates[j][2], candidates[n-1][2]):
                    # compute contour of induced polygon
                    candidate_contour = bounds_to_polygon([candidates[i][0], candidates[i][2][0],
                                                           candidates[j][2][0], candidates[j][0],
                                                           candidates[j][2][1], candidates[i][2][1]], data.contour)
                    # rotate contour and add first point to create Polygon object
                    rotated_candidate_contour = rotate_contour(candidate_contour, candidates[j][0], candidates[j][2])
                    # new_rotated_candidate_contour = rotated_candidate_contour + rotated_candidate_contour[0]
                    candidate_polygon = Polygon(rotated_candidate_contour)
                            
                    candidate_polygon_aspectratio = compute_aspectratio(candidate_polygon)
    
                    #check if polygon is feasible (has right size) and add candidate polygon to list of feasible cuts
                    if min_area <= candidate_polygon.area <= max_area:
                        if opt == 'min_num':
                            feasible_cuts.append((check[j]+1, j, candidate_polygon))
                        elif opt == 'max_fat':
                            if j == n-1:
                                optimal_aspectratio = candidate_polygon_aspectratio
                            else:
                                optimal_aspectratio = min(check[j], candidate_polygon_aspectratio)
                            feasible_cuts.append((optimal_aspectratio, j, candidate_polygon))
        # if feasible cuts are found, compute the optimal cut
        if feasible_cuts:
            if opt == 'min_num':
                sorted_cuts = sorted(feasible_cuts, key=lambda cut: cut[0])
            elif opt == 'max_fat':
                sorted_cuts = sorted(feasible_cuts, key=lambda cut: cut[0], reverse=True)
            else:
                return []
            opt_value = sorted_cuts[0][0]
            opt_candidate = sorted_cuts[0][1]
            opt_polygon = sorted_cuts[0][2]

            check[i] = opt_value
            cuts[i] = [opt_candidate, opt_polygon]
        else:
            check[i] = math.inf

    # if polygon has a decomposition, add cut polygons to list
    if check[0] is not math.inf:
        decomposition_polygons = []
        next_poly = True
        next_index = 0
        while next_poly:
            if cuts[next_index][1] is not None:
                decomposition_polygons.append(cuts[next_index][1])
            if cuts[next_index][0] is None:
                next_poly = False
            else:
                next_index = cuts[next_index][0]
        return decomposition_polygons
    else:
        return []