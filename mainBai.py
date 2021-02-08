"""
@author: leosel
"""

from os import path

from ReadBaiData import read_data
from Graph import *
from Decomposition import *


def execute_decomposition(filepath):
    if path.exists(filepath):
        try:
            input_data = read_data(filepath)
            data = SkelData(input_data)
            #A = data.branchingpoints
            #print(A)
            #data.plot_contour()
            #data.plot_branchingpoints()
            data.get_all_dir()
            data.check_directions()

            #plt.show()
        except:
            print("execute decomposition failed")


#if __name__ == '__main__':
"""
manual_input = input("Input manually? (y/n)")

if manual_input == "y":
    filepath = input("input filepath:")
    min_area = input("input lower area bound:")
    max_area = input("input upper area bound:")
else:
"""
filepath = 'D:\\Neuer Ordner\\T13\\object_6_8.mat'
min_area = 100
max_area = 2800

input_data = read_data(filepath)
data = SkelData(input_data)
data.get_all_dir()
print(data.branchingpoints)
data.build()
P = decomposition(data,min_area,max_area)
#color = random_colors(len(data.edges))
#for i in range(len(data.edges)):
#    data.edges[i].plot(color[i],3)
#data.plot_skeleton()
#plt.show()
#data.plot_contour()
#data.plot_skeleton()
#plt.show()

