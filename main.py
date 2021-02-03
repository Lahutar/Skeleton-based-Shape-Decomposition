# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 09:08:19 2019

@author: leosel
"""
from ReadData import *
from Graph import *
from Partition import *
from ReadFrag import * 

from smallestenclosingcircle import *
from sympy import *
#results = [os.path.join(os.getcwd(), i) for i in os.listdir(os.getcwd()) if i.endswith('.mat')]
import numpy as np
import scipy as sp
from sympy import *

from matplotlib.path import Path

from shapely.geometry import Polygon
from shapely.ops import triangulate


from PIL import Image,ImageDraw
#print(data.skel_size())
#import scipy.io
#import h5py

import matplotlib.pyplot as plt
import csv

"""
def mat_to_list(mat,trans = True):
    new_list = []
    if trans:
        mat = mat.T
    for i in range(len(mat)):
        new_list.append((mat[i][0],mat[i][1]))
        
    return new_list

def part_to_list(part):
    partition = []
    for i in part:
        p1 = i.tolist()
        p2 = p1[0].tolist()
        p3 = mat_to_list(p2,False)
        partition.append(p3)
    return partition
"""

#if __name__ == '__main__':

filepath = 'C:\\Users\\LeoSel\\sciebo\\Daten\\skeldecomp\\Daten\\T1\\skel\\object_0_7.mat'

mina = 100
maxa = 2800

input_data = read_data(filepath)
data = SkelData(input_data)

print('area = ', data.object_area())
print('contour length = ', data.object_size())
print('branching = ',len(data.branchingpoints))
print('endpoints = ',len(data.endpoints))




partition_area = 0 

error = data.build_graph()
data.plot_image()
if error[0]:
    if mina <= data.object_area() <= maxa:
        partition = data.contour
        a = len(partition)
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(a)]
        for i in range(len(partition)):
            partition_area = partition_area + polygon_area(partition[i])
            #print("partition polygon area = ", polygon_area(partition[i]))
            plot_polygon(partition[i],color[i])  
            
            #plt.savefig(filepath.replace('.mat', str((mina,maxa))+'.svg'),format='svg', dpi=1200)
            #plt.savefig(filepath.replace('.mat', str((mina,maxa))+'.png'),format='png', dpi=1200)
            
          #  with open(obj.replace('.mat',str((mina,maxa))+'.txt'), "w") as filehandle:
          #      for item in partition:
          #          filehandle.write('%s\n' % item) 


if data.error:
    print(data.error) 
    if mina <= data.object_area() <= maxa:
        partition = data.contour
        a = len(partition)
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(a)]
        for i in range(len(partition)):
            partition_area = partition_area + polygon_area(partition[i])
            #print("partition polygon area = ", polygon_area(partition[i]))
            plot_polygon(partition[i],color[i],3)  
            
            #plt.savefig(filepath.replace('.mat', str((mina,maxa))+'.svg'),format='svg', dpi=1200)
            #plt.savefig(filepath.replace('.mat', str((mina,maxa))+'.png'),format='png', dpi=1200)
 
else:
    data.plot_skelbranches()
    try:
       # branch = data.edges[0]
        partition = linear_partition(data,mina,maxa)
        
        #print('number branches = ', len(data.edges))
        #partition = linear_partition(data,mina,maxa)
        
        if partition:
            a = len(partition)
            print("partition size = ", a)
            color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(a)]
            for i in range(len(partition)):
                partition_area = partition_area + polygon_area(partition[i])
                #print("partition polygon area = ", polygon_area(partition[i]))
                plot_polygon(partition[i],color[i],3)  
            
            #plt.savefig(filepath.replace('.mat', str((mina,maxa))+'.svg'),format='svg', dpi=1200)
            #plt.savefig(filepath.replace('.mat', str((mina,maxa))+'.png'),format='png', dpi=1200)
            
          #  with open(obj.replace('.mat',str((mina,maxa))+'.txt'), "w") as filehandle:
          #      for item in partition:
          #          filehandle.write('%s\n' % item) 
        
        print("partitioned area = ", partition_area, " that are ", (partition_area*100/data.object_area()), " %")
        
    except:
        print('partition not successful')
"""

filepath = 'C:\\Users\\LeoSel\\sciebo\\Daten\\skeldecomp\\Daten\\T6\\matfrag\\object1_1.mat'

mina=6
maxa =2778 

csv_path = filepath.replace('object1_1.mat',str((mina,maxa))+'.csv')

n = 41
infos =[]


for i in range(1,n):
    path = filepath.replace('object1_1', 'object1_'+str(i))
    
    contour, partition = read_frag(path)
    
    contour = contour[:-1]
    fig = plt.figure()
    plot_polygon(contour)
    P = Polygon(contour)
    object_area = P.area
    print(P.area)
    
    partition_area = 0 
    
    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(len(partition))]
    for i in range(len(partition)):
        P = Polygon(partition[i])
        partition_area = partition_area + P.area
        print(P.area)
        print("partition polygon area = ", P.area)
        plot_polygon2(partition[i],color[i],3)  
    
    
    ratio = format((partition_area*100/object_area), '.2f')
    print("partitioned area = ", partition_area, " that are ", ratio , " %")
    plt.savefig(path.replace('.mat', str((mina,maxa))+'.svg'),format='svg', dpi=1200)
    plt.savefig(path.replace('.mat', str((mina,maxa))+'.png'),format='png', dpi=1200)
    plt.show()
    plt.close(fig)
    
    infos.append([object_area, len(contour), len(partition),partition_area,ratio])
        
with open(csv_path, "w") as csvfile:
        fieldnames = ['area', 'size', 'partition size', 'partition area', 'ratio']
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
        writer.writeheader()
        for  i in range(1,n):
           writer.writerow({'area': infos[i-1][0], 'size': infos[i-1][1], 'partition size': infos[i-1][2], 'partition area':infos[i-1][3], 'ratio':infos[i-1][4]})

        



with open(filepath.replace('.mat',str((mina,maxa))+'.csv'), "w") as csvfile:
    fieldnames = ['area', 'size', 'partition size', 'partition area', 'ratio']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()
    writer.writerow({'area': object_area, 'size': len(contour), 'partition size': len(partition), 'partition area': partition_area, 'ratio': ratio})


obj = 'Daten\T6\object1_3.mat'

arrays = {}
f = h5py.File(obj)
for k,v in f.items():
    arrays[k]=np.array(v)
    
mat_contour = arrays['original']
contour=mat_to_list(mat_contour)

mat_partition = arrays['partitions']
partition = mat_partition.T

P = list()
for i in range(f['partitions'].maxshape[1]):
    h5part = f[f['partitions']][0][i]
    temp_tuple = tuple(map(tuple,h5part))
    temp_zip = zip(temp_tuple[0],temp_tuple[1])
    P.append(tuple(temp_zip))


plot_polygon2(contour)

P = Polygon(contour)

print(P.area)

#f = h5py.File('Daten\T6\object1.mat','r')
#data = f.get('data/original')


mat = scipy.io.loadmat('Daten\T6\object3.mat')
mat_contour = mat['original']
mat_partition = mat['partitions']

#b = mat_partition2[0]
#b2 = b.tolist()
#A = part_to_list(mat_partition2)


contour=mat_to_list(mat_contour,False)

plot_polygon2(contour)

P = Polygon(contour)

print(P.area)

object_area = P.area
print('object area = ', object_area)

partition = part_to_list(mat_partition)

partition_area = 0 

color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(len(partition))]
for i in range(len(partition)):
    P = Polygon(partition[i])
    partition_area = partition_area + P.area
    print(P.area)
    print("partition polygon area = ", P.area)
    plot_polygon2(partition[i],color[i],3)  

print("partitioned area = ", partition_area, " that are ", (partition_area*100/object_area), " %")
"""

"""
x, y = contour.T

fig = plt.figure(1)
ax = fig.add_subplot(111)
ax.plot(x, y, color='#6699cc', alpha=0.7,
    linewidth=2, solid_capstyle='round', zorder=2)
plt.axis('scaled')
"""
#plt.scatter(x,y)
#plt.show()

#plot_polygon(contour)
#data = SkelData(input_data)


"""



mina = 100
maxa = 200


"""


"""
polygon = input_data[1]
#plot_polygon(polygon)
P = Polygon(polygon)
P1 = P.exterior.coords
#plot_polygon(P1)
print(P.area)
bounds = P.bounds
polygon2 = []
for i in range(len(polygon)):
    polygon2.append((polygon[i][0]-bounds[0],polygon[i][1]-bounds[1]))
    
plot_polygon(polygon2)

width = 3360
height = 2400
img = Image.new('L', (width, height), 0)
ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
mask = np.array(img)


nx,ny = 2400,3360
x,y = np.meshgrid(np.arange(nx),np.arange(ny))
x,y = x.flatten(),y.flatten()

points = np.vstack((x,y)).T

path = Path(polygon)
grid = path.contains_points(points)
grid = grid.reshape((nx,ny))



width, height = int(bounds[2]-bounds[0]+2),int(bounds[3]-bounds[1]+2)
poly_path = Path(polygon2)

y,x = np.mgrid[:height, :width]
coors=np.hstack((x.reshape(-1, 1), y.reshape(-1,1))) # coors.shape is (4000000,2)

mask = poly_path.contains_points(coors)
mask2 = mask.reshape(height,width)
plt.imshow(mask.reshape(height, width))
plt.show()
dist2 = sp.ndimage.morphology.distance_transform_edt(mask2)
max_dist2 = np.amax(dist2)

dist= sp.ndimage.morphology.distance_transform_edt(shape)
max_dist= np.amax(dist)
"""




#liste = [(0,0),(1,0),(5,1),(0,1)]

#p1,p2,p3,p4 =[(0,0),(1,0),(5,1),(0,1)]
#P1 = Polygon(p1,p2,p3,p4)


#N = data.nodes
#B = data.edges
#B[0].edge_to_poly(data.contour)

#contour = B[1].poly_contour
#P = Polygon(*contour)
#print(-P.area)
#B[5].plot_poly()

#area1 = polygon_area(contour)
#color = "blue"
#plt.figure(1)
#plt.subplot(111)
#plt.plot([p[0] for p in contour],[p[1] for p in contour], c=color, alpha = 0.7)
#last = contour[-1:]+contour[0:1]
#plt.plot([p[0] for p in last],[p[1] for p in last], c=color, alpha=0.7)
#plt.axis('scaled')

#C = make_circle(contour)
#circle1 = plt.Circle((C[0],C[1]), C[2], color='r')
#plt.gcf().gca().add_artist(circle1)
#area = math.pi*C[2]*C[2]



#A = find_candidates(data,B[5])
"""
partition =  linear_partition(data,100,5000)
if partition:
    a = len(partition)
    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(a)]
    for i in range(len(partition)):
        plot_polygon(partition[i],color[i])
"""
          
            
#
#edge = B[0]
#polygon = Polygon(data.contour,edge.node_from.coords,edge.bound_from,edge.node_to.coords,edge.bound_to)
#polygon = Polygon(data.contour,(1902,752),(663,758),(1899,735),(685,750))
#plot_polygon(polygon.contour)
#a = polygon.area
"""
if error[0] == False:
    partition = linear_partition(data,100,3000)
    if partition:
        a = len(partition)
        color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(a)]
        for i in range(len(partition)):
            plot_polygon(partition[i],color[i])
"""
#else:
#    print(error)

#print(polygon.contour)
#plot_polygon(polygon.contour)
#partition = partition(data,0,1000)

#plot_polygon(partition[0][i])


#for b in B:
#    print(b.branch[0].coords,b.branch[1].coords)
#for n in data.nodes():
#    if n.branching == True:
#        print()
#print(data.error_check())
#for n in data.nodes:
#    print(n.coords)
#data.plot_skelbranches()
#data.plot_skel()
#P = partition(data,200,500)

"""        
contour_x = [p[0] for p in contour]
        contour_y = [p[1] for p in contour]
        poly_area = 0.5*np.abs(np.dot(contour_x, np.roll(contour_y, 1)) - np.dot(contour_y, np.roll(contour_x, 1)))        
        #print(poly_area)
        if poly_area < 1500:
            k = 1
        elif 1500 <= poly_area <= 10000:
            k = 2
        else:
            k = 3
        skel_error = False
        for i in nodes2:
            if i in skel_list:    
                if len(skel_dict[skel_list.index(i)]) < 3:
                    skel_error = True
                    print('not enough contact points')
            else:
                skel_error = True
                print('point missing in list')
        #if skel_error == False:
        area.append([poly_area,k])
    #area = sorted(area)
        
       else:
            tree = Tree(contour,B,nodes2,endpoints2,nodes2[0],skel_dict,skel_list)
        
            mina = 100 
            maxa = 5000#50000/4.25
            #opt = 0
            #near = False 
            
            tree.plot_tree()
            #tree.get_tree()
            #print(tree.r.vertex)
            #tree.r.listc[2].bounds = [67,12,56]
            #tree.compute_bounds(tree.r.listc[2].listc[0])
            b = tree.compute_bounds(tree.r)
            #print(b)
            #v=tree.r.listc[1].listc[0]
            #print(v.find_bounds(v.listc[1]))
            
            #print(tree.r.compute_bounds())
           
            #plt.axis('scaled')
            
            if b:
                try:
                    cuts = tree.decomp_tree(mina,maxa)
                    cut_list = cuts[0]
                    cut_dict = cuts[1]
                    
                    #a = np.linspace(0,1,len(cut_list2))
                    a = len(cut_list)
                    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(a)]
                    #cut_list.append(cut_list2)
                    #print(len(cut_list2))
                    
                    for i in range(a):
                             x = cut_dict[i][0][:,0]
                             y = cut_dict[i][0][:,1]
                             #plt.plot(x,y,c=(a[i],0,a[i]))
                             #color = list(np.random.choice(range(256), size=3))
                             plt.plot(x,y,color[i])
                    
                    
                    plt.savefig(obj.replace('.mat', str((mina,maxa))+'.svg'),format='svg', dpi=1200)
                    plt.savefig(obj.replace('.mat', str((mina,maxa))+'.png'),format='png', dpi=1200)
                    #k = cut_list2
                    with open(obj.replace('.mat','.txt'), "w") as filehandle:
                        for item in cut_list:
                            filehandle.write('%s\n' % item) 
                        
                        
                except:
                    print('error')
                    
        #k = cut_list               
        #with open('test.txt', "w") as filehandle:
             #for item in k:
                 #filehandle.write('%s\n' % item) 
"""  