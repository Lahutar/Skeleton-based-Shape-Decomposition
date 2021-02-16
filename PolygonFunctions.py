"""
@author: leosel
"""

import matplotlib.pyplot as plt
import numpy as np
import random


def random_colors(number_of_colors):
    color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(number_of_colors)]
    return color


def plot_contour(contour, color='dimgray', lwidth=1):
    #plt.figure(1)
    plt.subplot(111)
    plt.plot([p[0] for p in contour], [p[1] for p in contour], c=color, linewidth=lwidth, alpha=0.7)
    last = contour[-1:] + contour[0:1]
    plt.plot([p[0] for p in last], [p[1] for p in last], c=color, linewidth=lwidth, alpha=0.7)
    plt.axis('scaled')
    #plt.show()


def plot_polygon(polygon, color='dimgray', lwidth=1):
    #plt.figure(1)
    plt.subplot(111)
    plt.plot([p[0] for p in polygon], [p[1] for p in polygon], c=color, linewidth=lwidth, alpha=0.7)
    # fig.axes.get_xaxis().set_visible(False)
    # fig.axes.get_yaxis().set_visible(False)
    #plt.axis('off')
    #plt.show()


def plot_points(inlist, color='blue', size=20):
    fig = plt.subplot(111)
    x = [p[0] for p in inlist]
    y = [p[1] for p in inlist]
    fig.scatter(x, y, c=color, s=size)
    #plt.show()


def polygon_area(contour):
    contour_x = [p[0] for p in contour]
    contour_y = [p[1] for p in contour]
    poly_area = 0.5 * np.abs(np.dot(contour_x, np.roll(contour_y, 1)) - np.dot(contour_y, np.roll(contour_x, 1)))
    return poly_area


"""
get 8-neighbors of a pixel 
"""
def nbr8(image, row, col):
    neighbors = []
    for i in range(row-1, row+2):
        for j in range(col-1, col+2):
            if (i, j) == (row, col):
                continue
            if image[i][j]:
                neighbors.append((i, j))
    return neighbors


def get_8neighbors(image, point):
    return nbr8(image, point[0], point[1])


"""
get 4-neighbors of a pixel
"""
def nbr4(image, row, col):
    neighbors = []
    if image[row-1][col]:
        neighbors.append((row-1, col))
    if image[row+1][col]:
        neighbors.append((row+1, col))
    if image[row][col-1]:
        neighbors.append((row, col-1))
    if image[row][col+1]:
        neighbors.append((row, col+1))
    return neighbors


def get_4neighbors(image, point):
    return nbr4(image, point[0], point[1])

