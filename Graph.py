"""
@author: leosel
"""
from PolygonFunctions import *
import math

"""
Create a rooted tree out of the skeleton, boundary and contact data.
The graph consists of 
1. Nodes corresponding to branching/end points in the skeleton.
2. Edges between the nodes
Both Nodes and Edges contain more information about the skeleton. 
All this is build and stored in the SkelData class.
"""

"""
class Node: 
    - coords (tuples of ints) = pixel coordinates of skeleton point
    - contactpoints (list of ints): list of contactpoints as indices of the countour
    - is_branching (boolean) = True if it is a branching point
    - is_end (boolean) = True if it is an end point
    - father (Node) = father node *
    - children (list of Nodes) = list of children *
    - fatherbranch (list of tuples) = list of coordinates of all skeletonpoints between the Node and its father *
*initialized with default value and set during the building of the tree 
"""
class Node:
    def __init__(self, coords, contactpoints, is_branching=False, is_end=False, radius=None):
        self.coords = coords
        self.contactpoints = contactpoints
        self.is_branching = is_branching
        self.is_end = is_end
        self.father = None
        self.children = []
        self.fatherbranch = []
        self.radius = radius


"""
class Edge:
    - node_from (Node): start node of Edge
    - node_to (Node): end node of Edge
    - skel (list): list of skeleton points between node_from and node_to
    - bound_from (tuple): tuple containing the 2 contact points of node_from corresponding to this edge 
        (as tuple of indices of the contour) *
    - bound_to (tuple): tuple containing the 2 contact points of node_to corresponding to this edge 
        (as tuple of indices of the contour) *
    - poly_contour (list of tuples): circular list of the polygon induced by the Edge*
*initialized with default value and can be computed after the tree is build
"""


class Edge:
    def __init__(self, node_from, node_to):
        self.node_from = node_from
        self.node_to = node_to
        self.skel = node_to.fatherbranch
        self.bound_from = None
        self.bound_to = None
        self.poly_contour = None

    """
    function that returns the contour of the polygon that is induced by the edge.
    """
    def edge_to_poly(self, con):
        if self.bound_from and self.bound_to:
            bounds = self.bound_from + self.bound_to
            if bounds[2] == bounds[3]:  # endbranch
                if bounds[0] <= bounds[2] and bounds[3] <= bounds[1]:
                    contour = [self.node_from.coords] + con[bounds[0]:(bounds[1] + 1)]
                else:
                    contour = [self.node_from.coords] + con[bounds[0]:] + con[:(bounds[1] + 1)]
            else:  # inner branch
                if bounds[0] > bounds[2]:  # end of circular list in between 1 and 2
                    contour = [self.node_from.coords] + con[bounds[0]:] + con[:(bounds[2] + 1)] + [
                        self.node_to.coords] + con[bounds[3]:(bounds[1] + 1)]
                elif bounds[1] < bounds[3]:  # end of circular list in between 4 and 5
                    contour = [self.node_from.coords] + con[bounds[0]:(bounds[2] + 1)] \
                              + [self.node_to.coords] + con[bounds[3]:] + con[:(bounds[1] + 1)]
                else:  # end of circular list somewhere else
                    contour = [self.node_from.coords] + con[bounds[0]:(bounds[2] + 1)] \
                              + [self.node_to.coords] + con[bounds[3]:(bounds[1] + 1)]
            self.poly_contour = contour
            return contour

    def plot(self, color='blue', l=1):
        plot_contour(self.poly_contour, color,l)


"""
Class for the skeleton graph (tree) that contains all important skeleton data
"""
class SkelData:
    def __init__(self, data):
        self.image = data[0]
        self.contour = data[1]
        self.endpoints = data[2]
        self.branchingpoints = data[3]
        self.skel_list = data[4]
        self.contact_dict = data[5]
        self.tree_root = None
        self.nodes = []
        self.edges = []
        self.error = []
        self.directions = []

    def plot_contour(self):
        plot_contour(self.contour)

    def object_area(self):
        object_area = polygon_area(self.contour)
        return object_area

    def plot_branchingpoints(self, color='blue', s=20):
        plot_points(self.branchingpoints, color, s)

    def plot_endpoints(self, color='blue', s=20):
        plot_points(self.endpoints, color, s)

    def plot_skeleton(self, color='green',l=1, s=20):
        for e in self.edges:
            plot_polygon(e.skel, color, l)
        self.plot_branchingpoints(color, s)
        self.plot_endpoints(color, s)

    """
    Bai skeletonization may result in skeleton that do not fulfill the necessary requirements for shape decomposition
    This function checks for common errors and stores them in the error variable
    """
    def error_check(self):
        skel_error = False
        #check if there are contact points for all skeleton points
        if len(self.skel_list) != len(self.contact_dict):
            skel_error = True
            self.error.append('list length error')
        #check if all end points are contained in the list of skeleton points
        if not set(self.endpoints).issubset(set(self.skel_list)):
            skel_error = True
            self.error.append('some endpoint not in skeleton list')
        #check if all branching points are contained in the list of skeleton points and have at least 3 contact points
        if set(self.branchingpoints).issubset(set(self.skel_list)):
            for p in self.branchingpoints:
                if len(self.contact_dict[self.skel_list.index(p)]) < 3:
                    skel_error = True
                    self.error.append("not enough contact points for branching point")
        else:
            skel_error = True
            self.error.append("some branching point not in skeleton list")
        return skel_error

    """
    get directions for traversal through skeleton. 
    direction contain
    a) 1 point if p is an end point
    b) 2 points if p is a normal point
    c) 3 points if p is a branching point
    """
    def get_dir(self, p):
        if p in self.branchingpoints:
            num = 3
        elif p in self.endpoints:
            num = 1
        else:
            num = 2
        directions = []

        n8 = get_8neighbors(self.image, p)
        n4 = get_4neighbors(self.image, p)

        if len(n8) == num:
            directions = n8.copy()
        elif len(n8) > num:
            if len(n4) == num:
                directions = n4.copy()
            elif len(n4) < num:
                directions = n4.copy()
                for q in list(set(n8)-set(n4)):
                    if q not in directions:
                        n4_q = get_4neighbors(self.image, q)
                        if n4_q is not None:
                            if set(n4_q).intersection(set(directions)) == set():
                                directions.append(q)
                        else:
                            directions.append(q)
            else:
                print(p)
                raise ValueError('warning: node with degree 4')
        if len(directions) < num:
            print(p)
            raise ValueError('not enough directions for node')
        elif len(directions) > num:
            print(p)
            raise ValueError('too many directions for node')

        return directions

    """
    function to get directions for all skeleton points. 
    """
    def get_all_dir(self):
        directions = [None]*len(self.skel_list)
        for i in range(len(self.skel_list)):
            dir = self.get_dir(self.skel_list[i])
            directions[i] = dir
        self.directions = directions

    """
    check if each point is contained in the directions of its directions
    """
    def check_directions(self):
        directions_error = False
        for i in range(len(self.directions)):
            for p in self.directions[i]:
                if self.skel_list[i] not in self.directions[self.skel_list.index(p)]:
                    directions_error = True
                    self.error.append('directions error')
        return directions_error

    """
    recursive function that build the tree from point p
    """
    def rec_build_tree(self, node, p, plist, visited):
        visited.add(p)
        new_directions = [x for x in self.directions[self.skel_list.index(p)] if x not in visited]
        # p is branching point: create new Node and build recursively in different directions
        if p in self.branchingpoints:
            if p is self.tree_root.coords:
                new_node = node
            else:
                new_node = Node(p, sorted(self.contact_dict[self.skel_list.index(p)]), True)
                plist.append(p)
                new_node.fatherbranch = plist
                node.children.append(new_node)
                new_node.father = node
                self.nodes.append(new_node)
                new_edge = Edge(node, new_node)
                self.edges.append(new_edge)
            if new_directions:
                for q in new_directions:
                    visited.update(self.rec_build_tree(new_node, q, [p], visited))
            else:
                raise ValueError("branching point without neighbors")
        # p is end point: create new Node and stop recursion
        elif p in self.endpoints:
            new_node = Node(p, sorted(self.contact_dict[self.skel_list.index(p)]), False,True)
            plist.append(p)
            new_node.fatherbranch = plist
            node.children.append(new_node)
            new_node.father =node
            self.nodes.append(new_node)
            new_edge = Edge(node, new_node)
            self.edges.append(new_edge)
            if new_directions:
                raise ValueError("end point with neighbors")
        # p is normal point: add to plist, find correct direction and move on
        else:
            plist.append(p)
            if len(new_directions) != 1:
                raise ValueError("normal point with too many neighbors")
            else:
                visited.update(self.rec_build_tree(node, new_directions[0], plist, visited))
        return visited

    """
    function to build skeleton tree
    choose arbitrary branching point (default first in list) as the root and build the graph recursively 
    """
    def build_tree(self):
        build_error = False
        self.get_all_dir()
        try:
            self.get_all_dir()
            if self.check_directions() is False:
                root = self.branchingpoints[0]
                self.tree_root = Node(root, sorted(self.contact_dict[self.skel_list.index(root)]), True, False)
                self.nodes.append(self.tree_root)
                visited = set()
                visited.update(self.rec_build_tree(self.tree_root, root, [], visited))
                if len(visited) != len(self.skel_list):
                    print('some points not visited')
        except ValueError as err:
            build_error = True
            print(err.args)
            self.error.append(err.args)
        return build_error

    """
    function to reduce the contact points of one node.
    the number should be equal to the degree of the node in the tree. 
    this function tries to find the right ones based on the contact points of the father and child nodes.
    If set_bounds is True, the computed contact points are assigned as bounds to the corresponding edges.
    """
    def rec_reduce_contactpoints(self, node, set_bounds=False):
        #generate list of tuples of successive contact points
        c = node.contactpoints
        c_tuples = []
        for i in range(1, len(c)):
            c_tuples.append((c[i-1], c[i]))
        c_last_tuple = (c[-1], c[0])

        #store father/child nodes and their contact points
        adj_nodes = []
        adj_contacts = []
        for n in node.children:
            adj_nodes.append(n)
            adj_contacts.append(n.contactpoints)
        if node.father:
            adj_nodes.append(node.father)
            adj_contacts.append(node.father.contactpoints)

        chosen_contact = []

        #for each adjacent node choose a tuple such that the contact points of the adjacent node
        # lie in between those two points. The tuple is deleted from the list.
        for i in range(len(adj_nodes)):
            if adj_nodes[i].is_branching is True:
                pointer = None

                # check the last tuple
                if c_last_tuple:
                    if adj_contacts[i][-1] <= c_last_tuple[1] or c_last_tuple[0] <= adj_contacts[i][0]:
                        pointer = math.inf
                    elif adj_contacts[i][0] <= c_last_tuple[-1] and c_last_tuple[0] <= adj_contacts[i][-1]:
                        pointer = math.inf

                # otherwise loop through the remaining tuples
                if pointer is None:
                    if c_tuples:
                        for j in range(len(c_tuples)):
                            if c_tuples[j][0] <= adj_contacts[i][0] and adj_contacts[i][-1] <= c_tuples[j][1]:
                                pointer = j

                # store chosen tuple and delete it from list
                if pointer is math.inf:
                    chosen_contact.append(c_last_tuple)
                    c_last_tuple = []
                elif pointer is not None:
                    chosen_contact.append(c_tuples[pointer])
                    c_tuples.pop(pointer)
                else:
                    raise ValueError("could not find suitable contact points for branching point")

            # adjacent end nodes may have multiple contact points but only one is chosen in the end
            # check which tuples would fit and choose one
            elif adj_nodes[i].is_end is True:
                pointers = [None] * len(adj_contacts[i])

                for k in range(len(adj_contacts[i])):
                    if c_last_tuple:
                        if adj_contacts[i][-1] <= c_last_tuple[1] or c_last_tuple[0] <= adj_contacts[i][0]:
                            pointers[k] = math.inf
                        elif adj_contacts[i][0] <= c_last_tuple[-1] and c_last_tuple[0] <= adj_contacts[i][-1]:
                            pointers[k] = math.inf

                    if pointers[k] is None:
                        if c_tuples:
                            for j in range(len(c_tuples)):
                                if c_tuples[j][0] <= adj_contacts[i][0] and adj_contacts[i][-1] <= c_tuples[j][1]:
                                    pointers[k] = j

                red_pointers = [x for x in set(pointers) if x is not None]

                if len(red_pointers) == 1:
                    if red_pointers[0] is math.inf:
                        chosen_contact.append(c_last_tuple)
                        c_last_tuple = []
                    else:
                        chosen_contact.append(c_tuples[red_pointers[0]])
                        c_tuples.pop(red_pointers[0])
                    for l in range(len(pointers)):
                        if pointers[l] is None:
                            adj_nodes[i].contactpoints.pop(l)
                else:
                    raise ValueError("could not find suitable contact points for end point")
            else:
                raise ValueError("some node is neither end nor branching point")

            #set bounds for connecting edges
            if set_bounds is True:
                e_from = [e for e in self.edges if (e.node_from == node and e.node_to == adj_nodes[i])]
                e_to = [e for e in self.edges if (e.node_from == adj_nodes[i] and e.node_to == node)]

                if len(e_from) == 1:
                    e_from[0].bound_from = chosen_contact[-1]
                    if adj_nodes[i].is_end is True:
                        adj_nodes[i].contactpoints = [adj_nodes[i].contactpoints[0]]
                        e_from[0].bound_to = (adj_nodes[i].contactpoints[0], adj_nodes[i].contactpoints[0])

                if len(e_to) == 1:
                    e_to[0].bound_to = (chosen_contact[-1][1], chosen_contact[-1][0])

        #set new contact points
        new_contact = sorted([x[0] for x in chosen_contact])
        node.contactpoints = new_contact

        #recursive execution for all children that have children (reduction for endpoints already done)
        if node.children:
            for childnode in node.children:
                if childnode.children:
                    self.rec_reduce_contactpoints(childnode, set_bounds)

    """
    function to start recursive reduction of contact points for all nodes
    """
    def reduce_contactpoints(self, set_bounds=False):
        reduce_error = False
        try:
            self.rec_reduce_contactpoints(self.tree_root, set_bounds)
        except ValueError as err:
            reduce_error = True
            print(err.args)
            self.error.append(err.args)
        return reduce_error

    """
    function to build skeleton tree and reduce all contact points
    2 executions of reduce_contactpoints: 1. to reduce the number, 2. to choose the right bounds for the edges 
    """
    def build(self):
        check_error = self.error_check()
        if check_error is False:
            build_error = self.build_tree()
            if build_error is False:
                reduce_error = self.reduce_contactpoints(False)
                if reduce_error is False:
                    self.reduce_contactpoints(True)
                    for e in self.edges:
                        e.edge_to_poly(self.contour)
