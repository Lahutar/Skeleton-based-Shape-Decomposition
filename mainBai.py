"""
@author: leosel
"""

import os
import glob
import csv

from ReadBaiData import read_data
from Graph import *
from Decomposition import *
from PolygonFunctions import *
from statistics import mean, median

from concurrent.futures import ThreadPoolExecutor
import time


def get_files_from_folder(folderpath):
    files = glob.glob(folderpath)
    files_ind = []
    for f in files:
        files_ind.append((f, int(f.split("_")[1])))
    files_ind = sorted(files_ind, key=lambda x: x[1])
    files = [x[0] for x in files_ind]
    return files


def save_object_infos(folderpath):
    files = get_files_from_folder(folderpath)
    csvpath = folderpath.replace('*.mat', 'info.csv')
    infos = []
    for filepath in files:
        input_data = read_data(filepath)
        data = SkelData(input_data)
        data_polygon = Polygon(data.contour)
        print([filepath.split("_")[1], len(data.contour), data.object_area(), compute_aspectratio(data_polygon),
               len(data.branchingpoints), len(data.endpoints), len(data.skel_list)])
        infos.append([filepath.split("_")[1], len(data.contour), data.object_area(), compute_aspectratio(data_polygon),
                      len(data.branchingpoints), len(data.endpoints), len(data.skel_list)])

    with open(csvpath, "w") as csvfile:
        fieldnames = ["index", "contour length", "area", "aspect ratio", "number skeletonpoints",
                      "number branching points", "number endpoints"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(infos)):
            writer.writerow({"index": infos[i][0], "contour length": infos[i][1], "area": infos[i][2],
                             "aspect ratio": infos[i][3], "number skeletonpoints": infos[i][4],
                             "number branching points": infos[i][5], "number endpoints": infos[i][6]})


def save_decomposition(result):
    print('saved: ', int(result[3].split("_")[1]))


"""
save decomposition as list of subpolygons (list of coordinates) to txt
result = [True, subpolygons, data, filepath, (min_area, max_area, opt, bridge_thresholds)]]
"""
def decomposition_to_txt(result, folderpath):
    object_name = result[3].split("_")[1]
    # if you want to save meta data in the filename
    #new_directory = folderpath.replace('*.mat', 'txt_output_'+str(result[4]))
    # if you want to have a simple output folder
    new_directory = folderpath.replace('*.mat', 'txt_output')
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    with open(new_directory+'\\'+object_name+'.txt', "w") as filehandle:
        for subpolgon in result[1]:
            filehandle.write('%s\n' % list(subpolgon.exterior.coords))


"""
plot the original polygon, the skeleton and the subpolygons from the decomposition
result = [True, subpolygons, data, filepath, (min_area, max_area, opt, bridge_thresholds)]]
"""
def plot_decomposition(result, folderpath):
    plt.clf()
    new_directory = folderpath.replace('*.mat', 'plot_output_' + str(result[4]))
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(len(result[1]))]
    for j in range(len(result[1])):
        result[2].plot_skeleton()
        result[2].plot_contour()
        plot_polygon(list(result[1][j].exterior.coords), color[j], 3)
    plt.savefig(new_directory+'\\'+result[3].split("_")[1]+'.png', format='png', dpi=600)
    #plt.savefig(new_directory + '\\' + result[3].split("_")[1] + '.pdf', format='pdf', dpi=600)
    #plt.savefig(new_directory + '\\' + result[3].split("_")[1] + '.svg', format='svg', dpi=600)
    plt.close()


"""
compute information about decomposition and save to 
result = [True, subpolygons, data, filepath, (min_area, max_area, opt, bridge_thresholds)]]
"""
def save_decomposition_info(result, folderpath):
    new_directory = folderpath.replace('*.mat', 'csv_output_' + str(result[4]))
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    with open(new_directory+'\\'+result[3].split("_")[1]+'_decomposition.csv', "w") as csvfile:
        fieldnames = ['area', 'size', 'aspect ratio']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(result[1])):
            area = result[1][i].area
            size = len(result[1][i].exterior.coords)
            aspect_ratio = compute_aspectratio(result[1][i])
            writer.writerow({'area': area, 'size': size, 'aspect ratio': aspect_ratio})

"""
execute decomposition algorithm on folder without multithreading
"""
def execute_decomposition_folder(folderpath, min_area, max_area, opt, bridge_thresholds):
    files = get_files_from_folder(folderpath)
    all_results = []
    time_results = []
    for f in files:
        tic = time.perf_counter()
        result = execute_decomposition(f, min_area, max_area, opt, bridge_thresholds)
        toc = time.perf_counter()
        #print("object ", len(all_results), f"in {toc-tic:0.4f}")
        all_results.append(result)
        if result[0]:
            time_results.append(round(toc-tic, 4))
    return all_results, time_results

"""
execute decomposition algorithm on folder with multithreading
"""
def execute_parallel_decomposition(filepath, min_area, max_area, opt, bridge_thresholds, cores=10):
    files = get_files_from_folder(filepath)
    executor = ThreadPoolExecutor(max_workers=cores)
    future_list = []
    time_result=[]
    for i in range(len(files)):
        future = executor.submit(execute_decomposition, files[i],  min_area, max_area, opt, bridge_thresholds)
        future_list.append(future)

    runtime = 0
    all_finished: bool = False
    executor.shutdown(wait=False)

    all_results = []
    saved = []

    while not all_finished:
        finished_count = 0
        error_count = 0

        for future in future_list:
            if future.done():
                finished_count = finished_count + 1
                e = future.exception()
                if e is None:
                    result = future.result()
                    if result[0]:
                        if result[1] not in saved:
                            all_results.append(result)
                            saved.append(result[1])
                            save_decomposition(result)
                            decomposition_to_txt(result, filepath)
                            #save_decomposition_info(result, filepath)
                            #plot_decomposition(result, filepath)
                    else:
                        error_count = error_count + 1
                else:
                    error_count = error_count + 1

        all_finished = finished_count == len(future_list)
        runtime = runtime +1
        print('finished: '+str(finished_count)+' out of '+str(len(future_list))+' in '+str(runtime)+' with error '+str(error_count))
        time.sleep(5)
        
    for future in future_list:
        e = future.exception()
        if e is not None:
            print(e)
    
    return all_results, time_result

"""
execute decomposition algorithm on single file
"""
def execute_decomposition(filepath, min_area, max_area, opt, bridge_thresholds):
    print('execute: ', int(filepath.split("_")[1]))
    if os.path.exists(filepath):
        try:
            input_data = read_data(filepath)
            data = SkelData(input_data)
            data.build()
            #depending on size
            if data.error:
                if min_area <= data.object_area() <= max_area:
                    subpolygons = [Polygon(data.contour)]
                    # if you want to distinguish the polygons that were not partitioned with the skeleton
                    #return [True, subpolygons, data, filepath, (min_area, max_area, 'whole')]
                    return [True, subpolygons, data, filepath, (min_area, max_area, opt, bridge_thresholds)]
                else:
                    return [False]
            else:
                if bridge_thresholds[1] is not math.inf or bridge_thresholds[2] is not math.inf:
                    if len(data.contour) > bridge_thresholds[1] or data.object_area() > bridge_thresholds[2]:
                        bridges = bridge_thresholds[0]
                    else:
                        bridges = 0
                else:
                    bridges = bridge_thresholds[0]

                subpolygons = decomposition(data, min_area, max_area, opt, bridges)
                return [True, subpolygons, data, filepath, (min_area, max_area, opt, bridge_thresholds)]
        except:
            print("execute decomposition failed")
            return [False]
    else:
        return [False]


#if __name__ == '__main__':
"""

manual_input = input("Input manually? (y/n)")

if manual_input == "y":
    filepath = input("input filepath:")
    min_area = input("input lower area bound:")
    max_area = input("input upper area bound:")
    opt = input("optimization goal: (min_num/max_fat)?")
    bridges = input("bridge width:")
    
    thresholds = input("Do you wish to add bridges based on thresholds? (y/n)")
    if thresholds == "y":
        contour_threshold = input("threshold on contour length:") 
        area_threshold = input("threshold on area:")
    else:
        contour_threshold = math.inf
        area_threshold = math.inf
    
    bridges_thresholds = [bridges, contour_threshold, area_threshold]

else:
    min_area = 100
    max_area = 2800
    opt = 'max_fat'
    bridges_thresholds = [0,math.inf,math.inf]
"""

min_area = 100
max_area = 2800
opt = 'max_fat'
bridges_thresholds = [0, math.inf, math.inf]

"""
decompose all files inside a folder
"""
filefolder = 'D:\\Neuer Ordner\\T12\\skel\\*.mat'
#save_object_infos(filefolder)

#execute_parallel_decomposition(filefolder, min_area, max_area, opt, bridges_thresholds)
start_time =  time.perf_counter()
#result, time_result = execute_decomposition_folder(filefolder, min_area, max_area, opt, bridges_thresholds)
result, time_result = execute_parallel_decomposition(filefolder, min_area, max_area, opt, bridges_thresholds)
end_time = time.perf_counter()
overall_time = round(end_time-start_time, 4)
print(overall_time)
def time_to_txt(time_result, overall_time, folderpath):
    with open(folderpath.replace('*.mat', 'multithread_time.txt'), "w") as filehandle:
        for i in range(len(time_result)):
            filehandle.write('%d\t%f s\n' % (i, time_result[i]))
        filehandle.write('\nSplit %d objects\n' % len(time_result))
        filehandle.write('Total time:\t%f s\n' % overall_time)
        filehandle.write('Time per object:\tMin: %f s\tMax: %f s\tMean: %f s\tMedian: %f s\n' % (min(time_result), max(time_result), mean(time_result), median(time_result)))

#time_to_txt(time_result, overall_time, filefolder)